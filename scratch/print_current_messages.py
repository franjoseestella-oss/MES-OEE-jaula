import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    print("Found overview.txt")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                # print any message coming from USER or USER_EXPLICIT or containing user query
                if data.get("source") in ["USER", "USER_EXPLICIT"] or data.get("type") == "USER_INPUT":
                    content = data.get("content") or data.get("query")
                    print(f"Line {i+1} [{data.get('created_at')}]: {content}")
            except Exception:
                pass
else:
    print("Log not found")
