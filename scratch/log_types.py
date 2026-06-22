import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print("Log file not found.")
    sys.exit(0)

types = {}
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            t = data.get("type")
            s = data.get("source")
            key = (s, t)
            types[key] = types.get(key, 0) + 1
        except Exception:
            pass

print("Types distribution:")
for k, v in types.items():
    print(f" - Source: {k[0]}, Type: {k[1]} (Count: {v})")
