import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\cbf08d14-19ca-4311-8710-0b0653a29a18\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("source") == "USER_EXPLICIT" and data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                if "<USER_REQUEST>" in content:
                    req = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                    print(f"[{data.get('created_at')}]: {req}")
                else:
                    print(f"[{data.get('created_at')}]: {content}")
        except Exception:
            pass
