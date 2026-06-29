import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/sql_diff_output.txt", "r", encoding="utf-16") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for idx, line in enumerate(lines):
    # Print the line, preserving its prefix
    print(f"{idx+1}: {line}", end="")
