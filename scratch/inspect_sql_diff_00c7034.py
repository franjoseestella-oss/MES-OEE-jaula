import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["git", "show", "00c7034", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

lines = result.stdout.splitlines()
for line in lines:
    if line.strip().startswith("+") or line.strip().startswith("-"):
        if not (line.strip().startswith("+++") or line.strip().startswith("---")):
            print(line)
