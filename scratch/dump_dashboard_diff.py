import subprocess

cmd = ["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

with open("scratch/dashboard_diff.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print("Diff written to scratch/dashboard_diff.txt")
