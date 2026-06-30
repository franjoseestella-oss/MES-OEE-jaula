import json

def extract_user_inputs(log_path, out_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    step = data.get("step_index")
                    content = data.get("content", "")
                    out_f.write(f"\n================ STEP {step} ================\n")
                    out_f.write(content + "\n")
            except Exception:
                pass

extract_user_inputs(
    r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt",
    r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\curr_user_inputs.txt"
)

extract_user_inputs(
    r"C:\Users\franj\.gemini\antigravity\brain\d0f2deca-f025-4511-8760-afada8897f63\.system_generated\logs\overview.txt",
    r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\prev_user_inputs.txt"
)

print("Done extracting user inputs")
