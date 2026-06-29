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
        query = next(p['targets'][0]['rawSql'] for p in data['panels'] if p.get('id') == 10)
        
        # Find the CASE WHEN ... END part
        idx = query.find("CASE \n            WHEN ft.t >=")
        if idx == -1:
            idx = query.find("CASE")
        
        print(f"=== COMMIT {commit} ===")
        # Print lines containing CASE/WHEN/THEN
        lines = query.splitlines()
        case_lines = [l for l in lines if "WHEN" in l or "THEN" in l or "CASE" in l or "ELSE" in l]
        for l in case_lines[-15:]:
            print(l)
    except Exception as e:
        print(f"Error for commit {commit}: {e}")
