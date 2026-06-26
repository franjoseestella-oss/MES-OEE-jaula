import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = subprocess.run(
    ["git", "diff", "HEAD", "grafana/provisioning/dashboards/plan_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

# Print first 2000 chars of diff or print lines that contain SELECT or DECLARE to see what queries changed
print(res.stdout[:5000])
if len(res.stdout) > 5000:
    print("... TRUNCATED ...")
