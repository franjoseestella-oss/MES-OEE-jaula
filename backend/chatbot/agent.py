"""Agente chatbot con Claude API y herramientas de consulta parametrizadas."""

import json
import logging
from typing import Optional

import anthropic

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
    if not settings.anthropic_api_key:
        return "Error: ANTHROPIC_API_KEY no configurada. Contacta al administrador."

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system = SYSTEM_PROMPT
    if machine_id_hint:
        system += f"\n\nLa máquina activa en pantalla es: {machine_id_hint}."

    # Aplanar historial al formato que espera Claude
    claude_messages = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role in ("user", "assistant"):
            claude_messages.append({"role": role, "content": content})

    # Bucle agentico: hasta MAX_ITERATIONS llamadas a herramientas
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=claude_messages,
        )

        # Respuesta final (sin uso de herramientas)
        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(text_blocks)

        # Procesar llamadas a herramientas
        if response.stop_reason == "tool_use":
            # Añadir respuesta del asistente al historial
            claude_messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                tool_name = block.name
                tool_input = block.input

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

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result_content, ensure_ascii=False, default=str),
                })

            claude_messages.append({"role": "user", "content": tool_results})

    return "No se pudo completar la consulta. Por favor, intenta reformular tu pregunta."
