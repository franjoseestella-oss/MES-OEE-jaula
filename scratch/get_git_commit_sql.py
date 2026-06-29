import subprocess
import json

# Get the JSON of the plan_dashboard.json at commit 7f0f72c
res_7f = subprocess.run(["git", "show", "7f0f72c:grafana/provisioning/dashboards/plan_dashboard.json"], capture_output=True, text=True, encoding="utf-8")
dash_7f = json.loads(res_7f.stdout)

# Get the JSON of the plan_dashboard.json at commit 0648ef1
res_06 = subprocess.run(["git", "show", "0648ef1:grafana/provisioning/dashboards/plan_dashboard.json"], capture_output=True, text=True, encoding="utf-8")
dash_06 = json.loads(res_06.stdout)

# Find Panel 10 queries
q_7f = ""
for p in dash_7f.get("panels", []):
    if p.get("id") == 10:
        q_7f = p["targets"][0]["rawSql"]
        break

q_06 = ""
for p in dash_06.get("panels", []):
    if p.get("id") == 10:
        q_06 = p["targets"][0]["rawSql"]
        break

print("--- PANEL 10 QUERY IN 7f0f72c ---")
print(q_7f)
print("\n\n--- PANEL 10 QUERY IN 0648ef1 ---")
print(q_06)
