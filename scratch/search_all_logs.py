import os
import json

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
convs = os.listdir(brain_dir)

for cid in convs:
    log_path = os.path.join(brain_dir, cid, ".system_generated", "logs", "overview.txt")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                try:
                    data = json.loads(line)
                    if data.get("source") == "USER_EXPLICIT":
                        content = data.get("content") or ""
                        if " el n " in content or " el n" in content or "notebook" in content.lower():
                            print(f"Match in conv {cid} line {i+1}:")
                            print(content.strip())
                            print("=" * 60)
                except Exception:
                    pass
