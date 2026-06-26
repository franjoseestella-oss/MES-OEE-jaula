import os
import sys

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

overview_file = r"C:\Users\franj\.gemini\antigravity\brain\e568e209-e1ec-4288-a6ca-6cc1d24b942c\.system_generated\logs\overview.txt"
if os.path.exists(overview_file):
    print("overview.txt exists, size:", os.path.getsize(overview_file))
    with open(overview_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print("Total lines:", len(lines))
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in ["active", "theoretical", "slot", "out_of_order", "anterior", "teorica"]):
            print(f"{i}: {line.strip()}")
else:
    print("overview.txt does not exist")
