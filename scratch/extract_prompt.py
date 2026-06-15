import json

path = r"C:\Users\franj\.gemini\antigravity\brain\c762074d-ed81-4662-b40b-7f25fa97514b\.system_generated\logs\overview.txt"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# find the line containing "genera una boton nuevo"
for line in lines:
    if "genera una boton nuevo" in line:
        data = json.loads(line)
        content = data["content"]
        with open("scratch/full_user_prompt.txt", "w", encoding="utf-8") as out:
            out.write(content)
        print("Successfully extracted full prompt to scratch/full_user_prompt.txt")
        break
