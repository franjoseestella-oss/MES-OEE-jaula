import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\d0f2deca-f025-4511-8760-afada8897f63\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if 1070 <= step_idx <= 1120:
                print(f"--- STEP {step_idx} ({data.get('type')}) ---")
                print(data.get("content", "")[:1000])
                print("-" * 50)
        except Exception as e:
            pass
