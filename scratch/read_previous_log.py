import sys
import os
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\ff73665e-0611-4498-9577-e0ed64617210\.system_generated\logs\overview.txt"
out_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\previous_log_tail.txt"

if not os.path.exists(log_path):
    print("Log does not exist at", log_path)
    sys.exit(1)

with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Write readable text representation of the last 150 lines
with open(out_path, 'w', encoding='utf-8') as f:
    for line in lines[-150:]:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            role = data.get("source", "UNKNOWN")
            content = data.get("content", "")
            f.write(f"[{role}]:\n{content}\n" + "-"*40 + "\n")
        except Exception as e:
            f.write(f"[RAW LINE ERR {e}]: {line}\n")

print(f"Tail written to {out_path}")

