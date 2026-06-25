import re

filepath = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\.system_generated\logs\overview.txt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(r"(?i)(desfase|eje|vertical|timeline|coincidir)", content):
    start = max(0, m.start() - 150)
    end = min(len(content), m.end() + 150)
    print(f"--- MATCH ---")
    print(content[start:end])
