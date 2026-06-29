import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/diff_between_commits.txt", "r", encoding="utf-16") as f:
    lines = f.readlines()

for line in lines:
    stripped = line.strip()
    if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
        # Let's clean it up slightly and print it
        print(line, end="")
