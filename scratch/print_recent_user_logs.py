import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\5fb9b6d4-078a-4d9e-b78a-22db34c6505a\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print("Log file not found.")
    sys.exit(0)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            # If the source is USER or if it has user messages
            if data.get("source") == "USER" or data.get("source") == "USER_EXPLICIT":
                print(f"[{data.get('created_at')}] {data.get('type')}: {data.get('content') or data.get('query') or data}")
        except Exception:
            pass
