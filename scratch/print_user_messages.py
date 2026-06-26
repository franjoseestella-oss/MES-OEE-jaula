import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\ff73665e-0611-4498-9577-e0ed64617210\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "USER" in str(data.get("source")) or data.get("type") == "USER_INPUT":
                    print(f"Line {i} {data.get('source')}:")
                    print(data.get("content"))
                    print("="*60)
            except Exception as e:
                pass
else:
    print("No log file found")


