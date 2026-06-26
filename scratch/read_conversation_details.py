import json
import os

conversations = ["5e6fce02-1734-4391-8a88-93b57b1083a0", "ff73665e-0611-4498-9577-e0ed64617210"]
keywords = ["completada", "proceso", "coja", "last completed", "active", "en curso", "secuencia"]

for cid in conversations:
    path = f"C:\\Users\\franj\\.gemini\\antigravity\\brain\\{cid}\\.system_generated\\logs\\overview.txt"
    if os.path.exists(path):
        print(f"\n=================== CONVERSATION: {cid} ===================")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            try:
                data = json.loads(line)
                content = data.get("content", "")
                if any(kw in content.lower() for kw in keywords):
                    print(f"[{data.get('type')}] Line {idx+1}: {content[:300]}")
            except Exception:
                # Fallback if line is not json
                if any(kw in line.lower() for kw in keywords):
                    print(f"[Raw] Line {idx+1}: {line[:300]}")
