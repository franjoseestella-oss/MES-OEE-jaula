import re

path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.system_generated\logs\overview.txt"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's find all user messages or recent actions
print("=== OVERVIEW TAIL ===")
lines = content.splitlines()
for line in lines[-150:]:
    if "USER:" in line or "user:" in line or "User:" in line or "User request:" in line or "objective" in line.lower() or "color" in line.lower() or "salte" in line.lower():
        print(line)

