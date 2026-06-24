with open("backend/api/routes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "@router." in line or "def " in line:
        print(f"Line {i+1}: {line.strip()}")
