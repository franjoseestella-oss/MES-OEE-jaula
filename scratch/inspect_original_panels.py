import json
import subprocess

original_data = subprocess.check_output(["git", "show", "HEAD:grafana/provisioning/dashboards/log_dashboard.json"]).decode("utf-8")
dashboard = json.loads(original_data)

for p in dashboard.get("panels", []):
    print(f"ID: {p.get('id')}, Title: {p.get('title')}, Type: {p.get('type')}")
