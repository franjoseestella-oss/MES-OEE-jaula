import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/diff_between_commits.txt", "r", encoding="utf-16") as f:
    lines = f.readlines()

print(f"Total lines in diff file: {len(lines)}")
for idx, line in enumerate(lines[:100]):
    print(f"{idx+1}: {line}", end="")
