import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = subprocess.run(
    ["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

# Search for options in panel 10 or orientation in the diff
diff_text = res.stdout
print("Is 'orientation' in the diff?", "orientation" in diff_text)
print("Is 'vertical' in the diff?", "vertical" in diff_text)
print("Is 'horizontal' in the diff?", "horizontal" in diff_text)

# Let's save the diff of panel 10 specifically
lines = diff_text.splitlines()
panel_10_lines = []
in_panel_10 = False
for line in lines:
    if 'Plan de Producción' in line:
        in_panel_10 = True
    if in_panel_10:
        panel_10_lines.append(line)
        if len(panel_10_lines) > 100:
            break

print("\n--- Panel 10 Diff snippet ---")
print("\n".join(panel_10_lines))
