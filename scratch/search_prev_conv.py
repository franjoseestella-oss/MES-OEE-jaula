import json
import re

log_path = r"C:\Users\franj\.gemini\antigravity\brain\d0f2deca-f025-4511-8760-afada8897f63\.system_generated\logs\overview.txt"

keywords = ["objetivo", "teorico", "turno", "recuadro", "red", "color", "calculate", "calcula", "imagen"]
pattern = re.compile("|".join(keywords), re.IGNORECASE)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            content = data.get("content", "")
            # check both content and tool_calls
            match = False
            if content and pattern.search(content):
                match = True
            
            if match and step_idx >= 800:
                print(f"--- STEP {step_idx} ({data.get('type')}) ---")
                print(content[:500] + "\n")
        except Exception:
            pass
