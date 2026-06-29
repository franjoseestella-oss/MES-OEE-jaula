import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["git", "diff", "HEAD", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

lines = result.stdout.splitlines()
in_sql = False
for idx, line in enumerate(lines):
    if '"rawSql"' in line:
        in_sql = True
    elif in_sql and line.strip().startswith('"') and not line.strip().startswith('"+"') and not line.strip().startswith('"-"'):
        if any(keyword in line for keyword in ['"refId"', '"datasource"', '"editorMode"']):
            in_sql = False
    
    if in_sql:
        continue
        
    stripped = line.strip()
    if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
        print(f"{idx}: {line}")
