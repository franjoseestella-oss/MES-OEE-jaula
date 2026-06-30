import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    print("Reading overview.txt...")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("source") == "USER" or data.get("type") == "USER_INPUT" or "salte" in line or "secuencia" in line:
                    print(f"[{data.get('created_at')}]: {data.get('content') or data.get('query') or line}")
            except Exception:
                if any(x in line for x in ["USER", "salte", "secuencia", "timeline"]):
                    print(line[:300])
else:
    print("Log path not found")
