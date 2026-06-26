import json
import os

conversations = ["5e6fce02-1734-4391-8a88-93b57b1083a0", "ff73665e-0611-4498-9577-e0ed64617210"]

for conv in conversations:
    log_path = f"C:\\Users\\franj\\.gemini\\antigravity\\brain\\{conv}\\.system_generated\\logs\\overview.txt"
    if os.path.exists(log_path):
        print(f"\n=== CONVERSATION {conv} ===")
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "USER" in data.get("source", ""):
                        print(f"[USER]: {data.get('content')}")
                except Exception as e:
                    pass
    else:
        print(f"Log not found: {log_path}")
