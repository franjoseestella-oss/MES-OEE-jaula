import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    count = 0
    for line in f:
        try:
            data = json.loads(line)
            if data.get("source") == "USER_EXPLICIT":
                print(data)
                count += 1
                if count >= 10:
                    break
        except Exception:
            pass
