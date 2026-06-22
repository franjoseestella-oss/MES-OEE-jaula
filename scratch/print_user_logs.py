import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print("Log file not found.")
    sys.exit(0)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            # If the source is USER or if it has user messages
            if data.get("source") == "USER" or "user" in str(data.get("type")).lower():
                print(f"[{data.get('created_at')}] {data.get('type')}: {data.get('content') or data.get('query') or data}")
        except Exception as e:
            pass
