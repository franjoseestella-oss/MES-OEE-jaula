import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/dashboard_diff_w.txt", "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

in_sql = False
for idx, line in enumerate(lines):
    if '"rawSql"' in line:
        in_sql = True
    elif in_sql and line.strip().startswith('"') and not line.strip().startswith('"+"') and not line.strip().startswith('"-"'):
        # End of rawSql string block
        if any(keyword in line for keyword in ['"refId"', '"datasource"', '"editorMode"']):
            in_sql = False
    
    if in_sql:
        continue
        
    stripped = line.strip()
    if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
        print(f"{idx}: {line}", end="")
