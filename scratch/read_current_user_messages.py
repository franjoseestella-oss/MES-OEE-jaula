import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get('source') == 'USER_EXPLICIT' or data.get('type') == 'USER_INPUT':
                    print(f"Step {data.get('step_index')}: {data.get('created_at')}")
                    print(data.get('content'))
                    print("=" * 40)
            except Exception as e:
                pass
