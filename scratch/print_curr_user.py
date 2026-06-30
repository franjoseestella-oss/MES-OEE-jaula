import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT" and data.get("status") == "DONE":
                print(f"=== STEP {data.get('step_index')} ===")
                print(data.get("content"))
                print()
        except Exception:
            pass
