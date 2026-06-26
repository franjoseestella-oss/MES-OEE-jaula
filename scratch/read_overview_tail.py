with open(r"C:\Users\franj\.gemini\antigravity\brain\e568e209-e1ec-4288-a6ca-6cc1d24b942c\.system_generated\logs\overview.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines[-100:]:
    print(line.strip())
