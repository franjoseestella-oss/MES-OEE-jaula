import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if 1820 <= step_idx <= 2250:
                print(f"\n--- STEP {step_idx} ({data.get('type')}) ---")
                if "content" in data and data["content"]:
                    print(data["content"])
                if "tool_calls" in data and data["tool_calls"]:
                    print("Tool Calls:")
                    for tc in data["tool_calls"]:
                        print(f"  {tc.get('name')}: {tc.get('args')}")
                if "output" in data and data["output"]:
                    out = data["output"]
                    if len(out) > 500:
                        print("Output (truncated):", out[:500])
                    else:
                        print("Output:", out)
        except Exception as e:
            pass
