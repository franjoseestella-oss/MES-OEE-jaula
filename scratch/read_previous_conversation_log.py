import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e\.system_generated\logs\overview.txt"

exchanges = []
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            source = data.get("source")
            etype = data.get("type")
            idx = data.get("step_index")
            body = data.get("content") or data.get("body") or data.get("query") or ""
            if source in ["USER_EXPLICIT", "MODEL"]:
                exchanges.append((idx, source, etype, body))
        except Exception:
            pass

print(f"Total exchanges: {len(exchanges)}")
for idx, source, etype, body in exchanges[-20:]:
    print(f"\n=== Step {idx} ({source} - {etype}) ===")
    print(body[:1000])
    print("-" * 50)
