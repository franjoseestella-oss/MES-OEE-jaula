import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

d = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774"
overview_path = os.path.join(d, ".system_generated", "logs", "overview.txt")
if os.path.exists(overview_path):
    with open(overview_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i >= 1000:
                try:
                    data = json.loads(line.strip())
                    if data.get("source") == "USER_EXPLICIT":
                        content = data.get("content", "").strip()
                        if content:
                            print(f"\n[USER MESSAGE - Line {i+1} - {data.get('created_at')}]:")
                            print(content)
                            print("-" * 50)
                except Exception:
                    pass
