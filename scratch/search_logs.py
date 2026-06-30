import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if "plan_dashboard" in line or "update_plan" in line or "test_value_case" in line:
                if step_idx > 500:
                    print(f"Step {step_idx} ({data.get('type')})")
                    if data.get("type") == "USER_INPUT" and data.get("content"):
                        print("  User Input:", data["content"][:200])
                    if data.get("type") == "PLANNER_RESPONSE" and data.get("tool_calls"):
                        for tc in data["tool_calls"]:
                            print("  Tool Call:", tc.get("name"), tc.get("args", {}).get("TargetFile") or tc.get("args", {}).get("CommandLine") or tc.get("args", {}).get("AbsolutePath") or "")
        except Exception as e:
            pass
