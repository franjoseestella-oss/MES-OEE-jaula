import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("scratch/dashboard_diff_w.txt", "r", encoding="utf-8-sig") as f:
    for line in f:
        stripped = line.strip()
        if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
            print(line, end="")
