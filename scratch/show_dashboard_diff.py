import subprocess

res = subprocess.run(["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"], capture_output=True, text=True)
print(res.stdout[:1500])
if len(res.stdout) > 1500:
    print("... truncated ...")
