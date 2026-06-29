import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/sql_diff_00c7034.txt", "r", encoding="utf-16") as f:
    lines = f.readlines()

print(f"Total diff lines: {len(lines)}")

# Let's print the first 100 lines and see
for i in range(min(100, len(lines))):
    print(lines[i].strip())
