import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print(f"Log path does not exist: {log_path}")
    # Let's list files in brain to see if we can find the correct directory
    brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
    if os.path.exists(brain_dir):
        print("Available brain directories:")
        print(os.listdir(brain_dir))
    sys.exit(1)

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines in previous log: {len(lines)}")
for i, line in enumerate(lines):
    try:
        obj = json.loads(line)
        content = obj.get("content", "")
        role = "USER" if obj.get("source") == "USER" else "MODEL"
        if content and len(content.strip()) > 0:
            print(f"[{i}][Step {obj.get('step_index')}] {role}: {content}")
    except Exception as e:
        pass
