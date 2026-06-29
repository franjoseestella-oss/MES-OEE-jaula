import subprocess
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's get the git log of plan_dashboard.json with patches to see previous modifications
cmd = ["git", "log", "-p", "-n", "10", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

# Let's write the history to a file so we can search it without console issues
with open("scratch/git_history_plan_dashboard.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print("Git log written to scratch/git_history_plan_dashboard.txt")
