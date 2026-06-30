import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if step_idx >= 1500:
                if data.get('type') == 'PLANNER_RESPONSE':
                    print(f"\n=== Step {step_idx} (PLANNER_RESPONSE) ===")
                    if "content" in data and data["content"]:
                        print("Content:", data["content"][:400])
                    if "tool_calls" in data and data["tool_calls"]:
                        for tc in data["tool_calls"]:
                            print("Tool Call:", tc.get("name"), tc.get("args", {}).get("TargetFile") or tc.get("args", {}).get("CommandLine") or tc.get("args", {}).get("AbsolutePath") or "")
                elif data.get('type') == 'USER_INPUT':
                    print(f"\n=== Step {step_idx} (USER_INPUT) ===")
                    if "content" in data and data["content"]:
                        print("Content:", data["content"])
        except Exception as e:
            pass
