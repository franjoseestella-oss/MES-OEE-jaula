import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["git", "diff", "00c7034..3f0671c", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

with open("scratch/diff_between_commits.txt", "w", encoding="utf-16") as f:
    f.write(result.stdout)

print("Diff size:", len(result.stdout))
# Print the non-SQL lines
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
        continue
    if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
        print(line)
