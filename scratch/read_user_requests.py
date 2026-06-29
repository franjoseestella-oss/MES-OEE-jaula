import json
import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\e568e209-e1ec-4288-a6ca-6cc1d24b942c\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                if data.get("source") == "USER_EXPLICIT":
                    print(f"--- Line {i+1} ---")
                    print(data.get("content"))
                    print("-" * 40)
            except Exception:
                pass
else:
    print("Log not found")
