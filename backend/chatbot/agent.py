"""Agente chatbot con Google Gemini API (gratuita) y herramientas de consulta parametrizadas."""

import json
import logging
from typing import Optional

from google import genai
from google.genai import types

from config import get_settings
from chatbot.tools import TOOL_DEFINITIONS, TOOL_HANDLERS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres un asistente especializado en MES/OEE para la planta de Logisnext.
Respondes SIEMPRE en español. Tu rol es ayudar a los operadores y supervisores a:
- Consultar el estado y rendimiento de las máquinas en tiempo real.
- Analizar el OEE (Disponibilidad, Rendimiento y Calidad) por turno, día o ventana de tiempo.
- Identificar causas de parada y tiempo perdido.
- Generar resúmenes y reportes del turno o del día.

Reglas:
1. Solo usas las herramientas disponibles para consultar datos. No inventas cifras.
2. Si no encuentras datos, dilo claramente y sugiere qué revisar.
3. Presentas los porcentajes de OEE redondeados a 1 decimal.
4. Para reportes de turno o día, estructura la respuesta con secciones claras.
5. Si el usuario pide un reporte exportable, formatea la respuesta como Markdown."""

MAX_ITERATIONS = 5


def _convert_tools_to_gemini() -> list[types.Tool]:
    """Convierte las definiciones de herramientas del formato Anthropic al formato Gemini."""
    function_declarations = []
    for tool_def in TOOL_DEFINITIONS:
        schema = tool_def["input_schema"].copy()
        # Gemini no usa 'required' al mismo nivel — lo inyectamos en properties
        func_decl = types.FunctionDeclaration(
            name=tool_def["name"],
            description=tool_def["description"],
            parameters=schema,
        )
        function_declarations.append(func_decl)
    return [types.Tool(function_declarations=function_declarations)]


def run_chat(
    messages: list[dict],
    machine_id_hint: Optional[str] = None,
) -> str:
    """Ejecuta un turno de conversación con el agente.

    Args:
        messages: Historial completo [{"role": "user"|"assistant", "content": str}, …]
        machine_id_hint: ID de máquina sugerido (para contexto de sistema)
    Returns:
        Respuesta textual final del asistente.
    """
    settings = get_settings()
    api_key = settings.gemini_api_key.strip() if settings.gemini_api_key else ""
    if not api_key or api_key == "tu_api_key_aqui":
        return (
            "⚠️ **Configuración de clave API requerida**\n\n"
            "Para conversar con el chatbot, necesitas configurar una clave API de Google Gemini **gratuita** en tu archivo `.env`:\n\n"
            "1. Ve a [Google AI Studio](https://aistudio.google.com/apikey) y crea una clave API gratis.\n"
            "2. Abre el archivo `.env` en la raíz del proyecto.\n"
            "3. Modifica la línea `GEMINI_API_KEY=tu_api_key_aqui` con tu clave real.\n"
            "4. Guarda el archivo (la aplicación se recargará automáticamente)."
        )

    try:
        client = genai.Client(api_key=api_key)
    except Exception as exc:
        logger.error("Error al inicializar cliente Gemini: %s", exc)
        return f"⚠️ **Error de inicialización:** No se pudo instanciar el cliente de Gemini ({exc})."

    system = SYSTEM_PROMPT
    if machine_id_hint:
        system += f"\n\nLa máquina activa en pantalla es: {machine_id_hint}."

    # Convertir herramientas al formato Gemini
    gemini_tools = _convert_tools_to_gemini()

    # Construir historial de mensajes para Gemini
    gemini_contents = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "user":
            gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=content)]))
        elif role == "assistant":
            gemini_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=content)]))

    # Configurar modelo y sus respaldos en caso de límite de cuota (429)
    primary_model = settings.gemini_model.strip() if getattr(settings, "gemini_model", None) else "gemini-2.0-flash"
    candidate_models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-flash-latest",
    ]
    current_model = primary_model

    # Bucle agéntico: hasta MAX_ITERATIONS llamadas a herramientas
    for _ in range(MAX_ITERATIONS):
        response = None
        # Lista ordenada de modelos a probar (empezando por el actual que funcionó o el primario)
        models_to_try = [current_model] + [m for m in candidate_models if m != current_model]
        
        last_exception = None
        for model_candidate in models_to_try:
            try:
                logger.info("Llamando a Gemini con modelo: %s", model_candidate)
                response = client.models.generate_content(
                    model=model_candidate,
                    contents=gemini_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        tools=gemini_tools,
                        temperature=0.3,
                    ),
                )
                # Si tiene éxito, fijamos este modelo para el resto de la conversación de este turno
                current_model = model_candidate
                break
            except Exception as exc:
                error_msg = str(exc)
                logger.error("Error con modelo %s: %s", model_candidate, error_msg)
                
                # Si el error es de clave de API inválida o filtrada, abortamos inmediatamente
                if "API_KEY" in error_msg.upper() or "401" in error_msg or "403" in error_msg or "LEAKED" in error_msg.upper():
                    return (
                        "⚠️ **Clave API no válida o filtrada (Leaked)**\n\n"
                        "La clave configurada en el archivo `.env` ha sido rechazada por Google "
                        "(posiblemente por haberse detectado su publicación en un repositorio público y haber sido revocada).\n\n"
                        "Por favor, sigue estos pasos para solucionarlo:\n"
                        "1. Ve a [Google AI Studio](https://aistudio.google.com/apikey) y crea una nueva clave API gratis.\n"
                        "2. Abre el archivo `.env` en la raíz de tu proyecto.\n"
                        "3. Modifica la línea `GEMINI_API_KEY=tu_api_key_aqui` con tu clave real.\n"
                        "4. Guarda el archivo y el servidor se reiniciará automáticamente."
                    )
                
                # Si es un error de cuota/límite de peticiones (429), probamos el siguiente modelo
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg.upper() or "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
                    logger.warning("El modelo %s devolvió error de cuota (429/RESOURCE_EXHAUSTED). Intentando modelo alternativo...", model_candidate)
                    last_exception = exc
                    continue
                else:
                    # Si es otro tipo de error, informamos y salimos para no ocultar bugs reales
                    return f"⚠️ **Error en el servicio de IA (Gemini):** {error_msg}"

        if response is None:
            # Si se probaron todos los modelos de la pool y todos fallaron con cuota
            if last_exception:
                return (
                    f"⚠️ **Error de Cuota/Límite en Gemini (429):** Se han agotado las solicitudes gratuitas en todos los modelos "
                    f"disponibles ({', '.join(models_to_try)}).\n\n"
                    f"Detalle del error original:\n`{str(last_exception)}`\n\n"
                    f"Por favor, espera un minuto o configura una clave API diferente o con facturación en tu `.env`."
                )
            return "⚠️ **Error en el servicio de IA:** Todos los modelos de Gemini fallaron al generar una respuesta."

        # Comprobar si hay llamadas a funciones
        has_function_calls = False
        function_call_parts = []
        text_parts = []

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    has_function_calls = True
                    function_call_parts.append(part)
                elif part.text:
                    text_parts.append(part.text)

        # Si no hay llamadas a herramientas, devolver texto
        if not has_function_calls:
            return "\n".join(text_parts) if text_parts else "No se pudo generar una respuesta."

        # Procesar llamadas a herramientas
        # Añadir respuesta del modelo al historial
        gemini_contents.append(response.candidates[0].content)

        # Ejecutar cada herramienta y recopilar resultados
        function_response_parts = []
        for part in function_call_parts:
            fc = part.function_call
            tool_name = fc.name
            tool_input = dict(fc.args) if fc.args else {}

            logger.info("Chatbot llama herramienta: %s(%s)", tool_name, tool_input)
            handler = TOOL_HANDLERS.get(tool_name)
            if handler is None:
                result_content = {"error": f"Herramienta '{tool_name}' no disponible."}
            else:
                try:
                    result_content = handler(tool_input)
                except Exception as exc:
                    logger.error("Error en herramienta %s: %s", tool_name, exc, exc_info=True)
                    result_content = {"error": str(exc)}

            function_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response=result_content,
                )
            )

        # Añadir resultados de las herramientas al historial
        gemini_contents.append(
            types.Content(role="user", parts=function_response_parts)
        )

    return "No se pudo completar la consulta. Por favor, intenta reformular tu pregunta."
