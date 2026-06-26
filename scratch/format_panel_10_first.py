import json

with open(r"C:\Users\franj\.gemini\antigravity\brain\ff73665e-0611-4498-9577-e0ed64617210\.system_generated\steps\2090\output.txt", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data:
    if p["title"] == "Plan de Producción por Secuencias (Teórico vs Real)":
        print("=== PANEL 10 QUERY FIRST 100 LINES ===")
        lines = p["query"].splitlines()
        for i, line in enumerate(lines[:120]):
            print(f"{i+1:3d}: {line}")
