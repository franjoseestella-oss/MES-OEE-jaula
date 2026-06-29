import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read with 'utf-16' which handles BOM automatically
with open("scratch/diff_plan.diff", "r", encoding="utf-16") as f:
    content = f.read()

with open("scratch/diff_plan_utf8.txt", "w", encoding="utf-8") as f:
    f.write(content)

print(f"File converted. Length: {len(content)}")
lines = content.splitlines()
# Print lines with changes to see what was replaced
for idx, line in enumerate(lines):
    if line.startswith("-") or line.startswith("+"):
        if not line.startswith("---") and not line.startswith("+++"):
            # Print index and the line, truncated to 120 chars
            print(f"{idx}: {line[:120]}")
