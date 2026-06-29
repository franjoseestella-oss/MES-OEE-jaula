import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                data = json.loads(line)
                src = data.get("source", "")
                if src.startswith("USER"):
                    content = data.get('content', '')
                    if any(k in content.lower() for k in ["color", "amarillo", "azul", "gris", "exceso"]):
                        print(f"[{src}]: {content}")
            except Exception:
                pass
else:
    print("Log path not found")
