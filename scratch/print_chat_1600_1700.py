import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
output_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\chat_1600_1700.txt"

with open(log_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out_f:
    for line in f:
        try:
            data = json.loads(line)
            step_idx = data.get("step_index", 0)
            if 1600 <= step_idx <= 1750:
                out_f.write(f"\n--- STEP {step_idx} ({data.get('type')}) ---\n")
                if "content" in data and data["content"]:
                    out_f.write(data["content"] + "\n")
                if "tool_calls" in data and data["tool_calls"]:
                    out_f.write("Tool Calls:\n")
                    for tc in data["tool_calls"]:
                        out_f.write(f"  {tc.get('name')}: {json.dumps(tc.get('args'))}\n")
                if "output" in data and data["output"]:
                    out_f.write("Output:\n" + data["output"][:2000] + "\n")
        except Exception as e:
            pass
print("Done")
