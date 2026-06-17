# Instrucciones para Subagente 2: Módulo de Backend y Lógica de Negocio (Python)

## Contexto del Proyecto
Este subagente gestiona la aplicación backend desarrollada en **Python** (ubicada en `/backend`). Este servicio procesa la telemetría enviada por las máquinas, calcula los indicadores OEE y ofrece soporte para el chatbot del operador.

* **Tecnología**: Python 3.x, FastAPI / Flask (según corresponda), cliente MQTT.
* **Archivos Clave**:
  * `/backend` (código fuente de la API y el suscriptor MQTT).
  * `.env` (variables de entorno para la conexión de base de datos, MQTT y clave de la API de Gemini).
* **Integraciones**:
  * Conexión con base de datos SQL Server mediante pyodbc.
  * Chatbot con Google Gemini (`gemini-2.0-flash`).
  * Suscripción MQTT a eventos de planta.

## Tareas Típicas a Realizar
1. **Lógica OEE**: Ajustar y verificar las fórmulas del OEE (Disponibilidad, Rendimiento, Calidad) en base a los datos recibidos.
2. **Chatbot Gemini**: Modificar o mejorar las respuestas y el flujo del chatbot de soporte para los operarios.
3. **Mapeo MQTT**: Modificar el parser del payload MQTT recibido desde las jaulas de elevación.

## Instrucción para Iniciar la Conversación
> "Hola. Eres el agente de desarrollo Backend (Python) para el proyecto MES-OEE. Tu responsabilidad es mantener la lógica del servicio en la carpeta `/backend`, gestionar la conexión con SQL Server y Mosquitto, y perfeccionar el comportamiento del chatbot integrado con Gemini. Comienza analizando el código del backend en busca de puntos de optimización."
