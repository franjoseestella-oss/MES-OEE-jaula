with open("scratch/plan_diff.patch", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines[:100]):
    print(f"{i+1}: {line[:100].rstrip()}")
