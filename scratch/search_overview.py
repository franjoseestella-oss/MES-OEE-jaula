import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if " n " in line or "notebook" in line or "el n" in line:
            try:
                data = json.loads(line)
                print(f"Line {i+1}: {data.get('source')} - {data.get('type')}")
                content = data.get("content") or data.get("body") or ""
                print(content[:500])
                print("-" * 50)
            except Exception:
                pass
