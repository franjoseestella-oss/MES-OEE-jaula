import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Get diff of plan_dashboard.json between 0648ef1^ and 0648ef1
res = subprocess.run(
    ["git", "diff", "0648ef1^", "0648ef1", "grafana/provisioning/dashboards/plan_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

lines = res.stdout.splitlines()
matching_lines = []
for i, line in enumerate(lines):
    if "Alarma" in line or "actual_start" in line:
        # print surrounding lines
        start = max(0, i - 10)
        end = min(len(lines), i + 10)
        print(f"--- Match at line {i} ---")
        for idx in range(start, end):
            print(f"{idx}: {lines[idx]}")
        print("="*40)
