import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/raw_show_00c7034.txt", "r", encoding="utf-16") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for idx, line in enumerate(lines[:100]):
    print(f"{idx}: {line.strip()}")
