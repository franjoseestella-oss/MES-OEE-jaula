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
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            if "USER" in str(data.keys()) or "USER" in str(data.values()) or "user" in str(data.get("source")).lower():
                print(f"Line {i} keys: {list(data.keys())}")
                # Print the whole dict representation
                print(f"  {data}")
                print("-" * 40)
        except Exception as e:
            pass
