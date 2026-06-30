import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

# Read JSON lines
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception:
    with open(log_path, 'r', encoding='utf-16') as f:
        lines = f.readlines()

print("Details around step 142:")
for line in lines:
    try:
        data = json.loads(line.strip())
        step = data.get('step_index')
        if 135 <= step <= 150:
            print(f"Step {step}: {data.get('source')} - {data.get('type')}: {data.get('content', '')}")
            if data.get("tool_calls"):
                print(f"  Tool Calls: {data.get('tool_calls')}")
    except Exception as e:
        pass
