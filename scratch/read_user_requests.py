import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

dirs = [
    r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774", # current
    r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e", # previous
]

for d in dirs:
    log_path = os.path.join(d, ".system_generated", "logs", "overview.txt")
    if os.path.exists(log_path):
        print(f"\n========================================\nCONVERSATION: {os.path.basename(d)}\n========================================")
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                try:
                    data = json.loads(line)
                    if data.get("source") == "USER_EXPLICIT":
                        print(f"\n[Line {i+1} - {data.get('created_at')}]:")
                        print(data.get("content", "").strip())
                        print("-" * 50)
                except Exception:
                    pass
    else:
        print(f"Log not found for {d}")
