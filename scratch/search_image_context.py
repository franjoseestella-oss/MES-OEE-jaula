import os
import glob
import json

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
log_files = glob.glob(os.path.join(brain_dir, "*", ".system_generated", "logs", "overview.txt"))

for log_path in log_files:
    conv_id = log_path.split(os.sep)[-4]
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("type") == "USER_INPUT" and data.get("status") == "DONE":
                        content = data.get("content", "")
                        if content and any(kw in content.lower() for kw in ["imagen", "image", "crop"]):
                            print(f"\n==========================================")
                            print(f"CONVERSATION: {conv_id} | STEP: {data.get('step_index')}")
                            print(f"==========================================")
                            print(content)
                except Exception:
                    pass
    except Exception as e:
        print(f"Error reading {log_path}: {e}")
