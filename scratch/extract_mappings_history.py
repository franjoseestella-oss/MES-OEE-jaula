import subprocess
import json

commits = ["92178e9", "4ce355c", "5856491", "b81e1f9", "0648ef1"]
for commit in commits:
    try:
        res = subprocess.run(
            ["git", "show", f"{commit}:grafana/provisioning/dashboards/plan_dashboard.json"],
            capture_output=True, text=True, encoding="utf-8"
        )
        data = json.loads(res.stdout)
        mappings = next(p['fieldConfig']['defaults']['mappings'] for p in data['panels'] if p.get('id') == 10)
        print(f"=== COMMIT {commit} ===")
        print(json.dumps(mappings, indent=2))
    except Exception as e:
        print(f"Error for commit {commit}: {e}")
