import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            source = data.get("source", "")
            if "USER" in source:
                print(f"Step {data.get('step_index')} ({source}): {data.get('content') or json.dumps(data)}")
        except Exception:
            pass
