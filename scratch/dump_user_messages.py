import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            if data.get("source") == "USER_EXPLICIT":
                content = data.get("content", "")
                # search for keywords
                print(f"Line {i+1}: {content.strip()}")
                print("="*40)
        except Exception as e:
            pass
