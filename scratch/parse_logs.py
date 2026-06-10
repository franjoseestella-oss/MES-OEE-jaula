import json
with open(r'C:\Users\franj\.gemini\antigravity\brain\ff5f29f1-c502-41f7-9e24-fb41f764e81e\.system_generated\logs\overview.txt', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'step_index' in line:
            try:
                data = json.loads(line)
                if data.get('step_index', 0) >= 668:
                    print(f"Step {data['step_index']} ({data.get('source')}):")
                    if data.get('content'):
                        print(data['content'])
                    if data.get('tool_calls'):
                        print(data['tool_calls'])
                    print("-" * 40)
            except Exception as e:
                pass
