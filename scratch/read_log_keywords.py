import re

overview_file = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\.system_generated\logs\overview.txt"
with open(overview_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find lines containing keyword
keywords = ["ActiveSlotIdx", "TheoreticalActiveSlotIdx", "capping", "out of order", "anterior", "teorica"]
for i, line in enumerate(lines):
    for kw in keywords:
        if kw.lower() in line.lower():
            # print surrounding lines
            print(f"--- Line {i} (keyword: {kw}) ---")
            start = max(0, i - 3)
            end = min(len(lines), i + 8)
            for j in range(start, end):
                prefix = "=> " if j == i else "   "
                print(f"{prefix}{j}: {lines[j].strip()}")
            print()
            break
