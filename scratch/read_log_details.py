import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            source = data.get("source")
            etype = data.get("type")
            idx = data.get("step_index")
            # If the step is a tool call to notebooklm, or if the model response mentions notebook, let's print it.
            body = str(data.get("body") or data.get("content") or data.get("query") or "")
            if "notebook" in body.lower() or "mcp_notebooklm" in body or "n" in body.lower():
                print(f"Step {idx} ({source} - {etype}):")
                print(body[:300])
                print("-" * 50)
        except Exception:
            pass
