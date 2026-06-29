import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ["git", "diff", "-w", "HEAD", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

lines = result.stdout.splitlines()
print(f"Total diff lines ignoring whitespace: {len(lines)}")
for idx, line in enumerate(lines):
    print(f"{idx+1}: {line}")
