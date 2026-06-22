import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

overview_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

with open(overview_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
patterns = [
    re.compile(r"update_dashboard", re.IGNORECASE),
    re.compile(r"transformations", re.IGNORECASE),
    re.compile(r"plan_dashboard", re.IGNORECASE),
    re.compile(r"save_dashboard", re.IGNORECASE),
]

for idx, line in enumerate(lines):
    if any(p.search(line) for p in patterns):
        print(f"--- Line {idx} ---")
        # Print surrounding context (2 lines before, 3 lines after)
        start = max(0, idx - 2)
        end = min(len(lines), idx + 4)
        for j in range(start, end):
            print(f"  {j}: {lines[j].strip()}")
        print("-" * 50)
