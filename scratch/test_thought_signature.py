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

models = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]
response = None
chosen_model = None

for m in models:
    try:
        print(f"Trying {m}...")
        response = client.models.generate_content(
            model=m,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                tools=tools,
                temperature=0.3,
            )
        )
        chosen_model = m
        print(f"Success with {m}!")
        break
    except Exception as e:
        print(f"Failed with {m}: {e}")
        time.sleep(2)

if not response:
    print("All models failed!")
    exit(1)

print("Response model role:", response.candidates[0].content.role)
for i, part in enumerate(response.candidates[0].content.parts):
    print(f"Part {i}: type={type(part)}")
    print(f"Part {i} data:", part)
    # Check if there is a thought_signature inside function_call or elsewhere
    if part.function_call:
        print("Function Call:", part.function_call)
        print("Function Call fields:", dir(part.function_call))
        try:
            print("Function Call JSON:", part.function_call.model_dump())
        except Exception as e:
            print("dump error:", e)

# Try appending to gemini_contents and calling again
gemini_contents.append(response.candidates[0].content)

# Append tool response
tool_response_parts = [
    types.Part.from_function_response(
        name="query_database",
        response={"rows": [{"FECHA_MONTAJE": "20260612"}]}
    )
]
gemini_contents.append(types.Content(role="user", parts=tool_response_parts))

print("\n=== Segunda llamada ===")
try:
    response2 = client.models.generate_content(
        model=chosen_model,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0.3,
        )
    )
    print("Success! Response2 text:", response2.text)
except Exception as e:
    print("Error on response2:", e)
