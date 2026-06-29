import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"

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
for idx, source, etype, body in exchanges[:10]:
    print(f"\n=== Step {idx} ===")
    # Find the corresponding line in the log file and print it raw
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("step_index") == idx:
                    print(json.dumps(data, indent=2))
                    break
            except Exception:
                pass
    print("-" * 50)
