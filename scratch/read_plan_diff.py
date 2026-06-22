import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                source = data.get("source")
                msg_type = data.get("type")
                # print any key/value that might contain the message text
                if source == "USER_EXPLICIT" or "USER" in str(source):
                    print(f"Line {idx} Step {data.get('step_index')}: {data}")
            except Exception as e:
                pass
else:
    print("Log not found.")
