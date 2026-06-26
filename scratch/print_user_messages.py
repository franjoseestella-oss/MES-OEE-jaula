import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

overview_file = r"C:\Users\franj\.gemini\antigravity\brain\e568e209-e1ec-4288-a6ca-6cc1d24b942c\.system_generated\logs\overview.txt"

with open(overview_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("source") == "USER_EXPLICIT":
                print(f"[{data.get('created_at')}]: USER REQUEST:\n{data.get('content')}\n")
        except Exception:
            pass
