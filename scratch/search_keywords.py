keywords = ["secuencia", "teorico", "teórico", "amarillo", "azul", "quites", "timeline", "registro"]

with open(r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e\.system_generated\logs\overview.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        # check if any keyword is in line
        if any(kw in line.lower() for kw in keywords):
            print(f"Line {i} matches:")
            print(line[:300] + "...")
