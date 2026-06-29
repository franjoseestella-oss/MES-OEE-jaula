import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\e568e209-e1ec-4288-a6ca-6cc1d24b942c\.system_generated\logs\overview.txt"

if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for idx in range(580, len(lines)):
        try:
            data = json.loads(lines[idx])
            content = data.get("content", "")
            tool_calls = data.get("tool_calls", [])
            print(f"--- L{idx} ({data.get('created_at')}) ---")
            if content:
                print(f"Content: {content[:200]}")
            if tool_calls:
                for tc in tool_calls:
                    print(f"Tool call: {tc.get('name')} with arguments: {str(tc.get('arguments'))[:150]}")
        except Exception as e:
            print(f"Error parsing line {idx}: {e}")
else:
    print("Log path does not exist")
