import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["git", "show", "00c7034", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

lines = result.stdout.splitlines()
in_sql = False
for line in lines:
    stripped = line.strip()
    if '"rawSql"' in line:
        in_sql = True
    elif in_sql and line.strip().startswith('"') and not line.strip().startswith('"+"') and not line.strip().startswith('"-"'):
        if any(keyword in line for keyword in ['"refId"', '"datasource"', '"editorMode"']):
            in_sql = False
    
    if in_sql:
        # Just check if it's an added/deleted SQL line, maybe print it if it's short, or just skip it
        if stripped.startswith("+") or stripped.startswith("-"):
            if not any(k in stripped for k in ["DECLARE", "SELECT", "INNER JOIN", "LEFT JOIN"]):
                print(f"SQL line: {line}")
        continue
        
    if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
        print(line)
