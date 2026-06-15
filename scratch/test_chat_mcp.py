import os
import time
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

tool_def = types.FunctionDeclaration(
    name="query_database",
    description="Ejecuta una consulta SQL SELECT en la base de datos y devuelve los resultados.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "sql_query": {"type": "STRING", "description": "Consulta SQL SELECT"}
        },
        "required": ["sql_query"]
    }
)

tools = [types.Tool(function_declarations=[tool_def])]

print("=== Probar chats ===")
chat = client.chats.create(
    model="gemini-2.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=tools,
        temperature=0.3,
        system_instruction="Responde siempre en español y usa query_database si es necesario."
    )
)

# Enviar mensaje
response = chat.send_message("¿Qué fechas de montaje existen en la tabla LOG_TABLA?")
print("Response text:", response.text)
print("Function calls:", response.function_calls)

if response.function_calls:
    # Esperar un momento para evitar 429
    print("Durmiendo 10 segundos para evitar 429...")
    time.sleep(10)
    
    # Simular ejecución de la función
    result = {"rows": [{"FECHA_MONTAJE": "20260612"}]}
    
    print("Enviando respuesta de función...")
    part = types.Part.from_function_response(
        name="query_database",
        response=result
    )
    
    response2 = chat.send_message(part)
    print("Response 2 text:", response2.text)

print("\nHistorial del chat:")
for msg in chat.get_history():
    print(f"Role: {msg.role}")
    for p in msg.parts:
        print(f"  Part: {p}")
