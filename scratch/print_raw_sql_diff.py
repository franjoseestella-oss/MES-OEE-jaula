import subprocess
import sys

if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

res = subprocess.run(["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"], capture_output=True)
stdout = res.stdout.decode('utf-8', errors='replace')
lines = stdout.splitlines()

for line in lines:
    if line.startswith('-') and 'rawSql' in line:
        print("MINUS:", line[:200])
    elif line.startswith('+') and 'rawSql' in line:
        print("PLUS :", line[:200])
