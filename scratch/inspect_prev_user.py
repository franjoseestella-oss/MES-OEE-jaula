import json

prev_log_path = r"C:\Users\franj\.gemini\antigravity\brain\d0f2deca-f025-4511-8760-afada8897f63\.system_generated\logs\overview.txt"

with open(prev_log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT" and data.get("status") == "DONE":
                print(f"=== STEP {data.get('step_index')} ===")
                print(data.get("content"))
                print()
        except Exception:
            pass
