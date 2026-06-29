import subprocess
import json

# Let's run git diff and capture the output
cmd = ["git", "diff", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

# Let's see if we can find lines related to panel 10 or colors in the diff
diff_lines = result.stdout.splitlines()
print(f"Total diff lines: {len(diff_lines)}")

# Let's search for "color" or "mapping" or "threshold" in the diff lines
for i, line in enumerate(diff_lines):
    if any(k in line for k in ["color", "mapping", "threshold", "Exceso de tiempo", "Alarma", "Esperando", "En proceso"]):
        # print context
        start = max(0, i - 5)
        end = min(len(diff_lines), i + 6)
        print(f"\n--- Context around line {i} ---")
        for j in range(start, end):
            prefix = ">>>" if j == i else "   "
            print(f"{prefix} {diff_lines[j]}")
