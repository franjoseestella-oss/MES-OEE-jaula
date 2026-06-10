import subprocess

result = subprocess.run(
    ["git", "show", "dc98fb2", "--", "grafana/provisioning/dashboards/log_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

lines = result.stdout.splitlines()
in_panel_15 = False
count = 0
for line in lines:
    if 'id": 15' in line:
        in_panel_15 = True
        idx = lines.index(line)
        for i in range(idx - 20, min(idx + 120, len(lines))):
            print(lines[i])
        break
