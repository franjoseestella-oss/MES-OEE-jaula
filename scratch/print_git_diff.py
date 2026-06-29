import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = subprocess.run(
    ["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)
print(res.stdout)
