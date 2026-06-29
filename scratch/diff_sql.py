import subprocess

cmd = ["git", "diff", "-w", "HEAD", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

with open("scratch/diff_utf8.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print("Diff size:", len(result.stdout))
