import subprocess

result = subprocess.run(
    ["git", "show", "0648ef1", "--", "grafana/provisioning/dashboards/plan_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

with open("scratch/git_show_0648ef1.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print("Saved git show to scratch/git_show_0648ef1.txt")
