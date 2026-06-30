import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if 1600 <= step_idx <= 1840:
                print(f"\n--- STEP {step_idx} ({data.get('type')}) ---")
                if "content" in data and data["content"]:
                    print(data["content"])
                if "tool_calls" in data and data["tool_calls"]:
                    print("Tool Calls:", data["tool_calls"])
                if "output" in data and data["output"]:
                    print("Output:", data["output"][:400])
        except Exception as e:
            pass
