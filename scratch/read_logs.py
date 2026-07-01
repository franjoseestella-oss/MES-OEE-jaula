import json

log_path = r"c:\Users\franj\.gemini\antigravity\brain\411c0de7-6105-4f4d-b8ba-9f5ddbbcfc27\.system_generated\logs\overview.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            step = data.get("step_index", 0)
            if 2000 <= step <= 3000:
                content = data.get("content", "")
                if data.get("type") in ("USER_INPUT", "PLANNER_RESPONSE") and (content or data.get("tool_calls")):
                    print(f"Step {step} ({data.get('source')}): {data.get('type')}")
                    if content:
                        print(f"Content: {content.strip()[:600]}")
                    if data.get("tool_calls"):
                        print(f"Tool calls: {data.get('tool_calls')}")
                    print("="*60)
        except Exception as e:
            pass
