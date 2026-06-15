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

gemini_contents = [
    types.Content(role="user", parts=[types.Part.from_text(text="¿Qué fechas de montaje existen en la tabla LOG_TABLA?")])
]

# Wait 10s to be safe
print("Sleeping 10s to clear rate limits...")
time.sleep(10)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0.3,
        )
    )
    print("Success with gemini-2.0-flash!")
    for i, part in enumerate(response.candidates[0].content.parts):
        print(f"Part {i}:")
        print("  text:", part.text)
        print("  function_call:", part.function_call)
        print("  thought:", getattr(part, 'thought', None))
        print("  thought_signature:", getattr(part, 'thought_signature', None))
        print("  model_fields_set:", part.model_fields_set)
        # Let's serialize it to see if it has thought_signature in JSON dict
        print("  model_dump:", part.model_dump(exclude_none=False))
except Exception as e:
    print("Error:", e)
