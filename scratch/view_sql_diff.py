import subprocess
import difflib

# Get the original rawSql from git
res_git = subprocess.run(["git", "show", "HEAD:grafana/provisioning/dashboards/plan_dashboard.json"], capture_output=True, text=True, encoding="utf-8")
import json
orig_data = json.loads(res_git.stdout)
orig_sql = ""
for p in orig_data.get("panels", []):
    if p.get("id") == 10:
        orig_sql = p["targets"][0]["rawSql"]
        break

# Get the current rawSql from file
with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    curr_data = json.load(f)
curr_sql = ""
for p in curr_data.get("panels", []):
    if p.get("id") == 10:
        curr_sql = p["targets"][0]["rawSql"]
        break

# Print the difference
diff = list(difflib.unified_diff(orig_sql.splitlines(), curr_sql.splitlines(), fromfile="original", tofile="current"))
for line in diff:
    print(line)
