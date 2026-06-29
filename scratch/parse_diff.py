import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

diff_path = "scratch/diff_utf8.txt"
with open(diff_path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's find sections related to plan_dashboard.json
# Since diff contains multiple files, let's extract the part for plan_dashboard.json
plan_diff_match = re.search(r"diff --git a/grafana/provisioning/dashboards/plan_dashboard\.json b/grafana/provisioning/dashboards/plan_dashboard\.json.*?(?=diff --git|$)", content, re.DOTALL)
if not plan_diff_match:
    print("Could not find plan_dashboard.json diff")
    sys.exit(0)

plan_diff = plan_diff_match.group(0)
lines = plan_diff.splitlines()

print(f"Diff of plan_dashboard.json has {len(lines)} lines")

# Print lines that look like deleted or added configurations for colors/mappings
for idx, line in enumerate(lines):
    if line.startswith("-") or line.startswith("+"):
        if any(keyword in line for keyword in ["color", "mapping", "threshold", "value", "Alarma", "Esperando", "Exceso", "En proceso", "Pausada", "Finalizada"]):
            # Print with some context
            print(f"{idx}: {line}")
