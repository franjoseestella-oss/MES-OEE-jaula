import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            # check both content and tool inputs/outputs
            step_str = json.dumps(data)
            if any(w in step_str.lower() for w in ["azul", "amarillo", "color"]):
                print(f"--- Step {data.get('step_index')} ({data.get('source')}, {data.get('type')}) ---")
                if content:
                    print(content)
                else:
                    print(step_str[:500])
        except Exception as e:
            pass
