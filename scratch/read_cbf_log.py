import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\cbf08d14-19ca-4311-8710-0b0653a29a18\.system_generated\logs\overview.txt"

if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"Total lines in previous log: {len(lines)}")
    # Print the last 100 lines
    for line in lines[-100:]:
        try:
            obj = json.loads(line)
            role = "USER" if obj.get("source") == "USER" else "MODEL"
            content = obj.get("content", "")
            if content and len(content.strip()) > 0:
                print(f"[{role}]: {content.strip()}")
        except Exception as e:
            pass
else:
    print("Log file does not exist")
