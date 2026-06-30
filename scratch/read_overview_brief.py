import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        # Since it might have JSON objects on multiple lines, let's load all of it and parse
        content = f.read()
        # Find all JSON blocks or split by lines, but wait, each line should be a separate JSON string?
        # Let's try splitting by lines first.
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get('source') == 'USER_EXPLICIT' or data.get('type') == 'USER_INPUT':
                    print(f"Step {data.get('step_index')}: {data.get('created_at')}")
                    print(data.get('content'))
                    print("-" * 50)
            except Exception as e:
                # If a line is not valid JSON, maybe the JSON spans multiple lines? Let's check.
                pass
else:
    print("Log file not found.")
