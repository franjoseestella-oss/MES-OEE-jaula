import subprocess
import json

# Let's list commits that modified log_dashboard.json
commits = subprocess.check_output(['git', 'log', '--oneline', '--', 'grafana/provisioning/dashboards/log_dashboard.json']).decode('utf-8').strip().split('\n')
print("Commits modifying log_dashboard.json:")
for c in commits:
    print(c)

# Let's inspect the threshold config in commit a42a05a, dc98fb2, 58b7cf2, 3c5863a
for commit_hash in ['a42a05a', 'dc98fb2', '58b7cf2', '3c5863a']:
    try:
        content = subprocess.check_output(['git', 'show', f'{commit_hash}:grafana/provisioning/dashboards/log_dashboard.json']).decode('utf-8', errors='ignore')
        d = json.loads(content)
        p15 = [p for p in d.get('panels', []) if p.get('id') == 15]
        if p15:
            print(f"\n--- Commit {commit_hash} Panel 15 fieldConfig ---")
            print(json.dumps(p15[0].get('fieldConfig', {}), indent=2))
            print("Transformations:")
            print(json.dumps(p15[0].get('transformations', []), indent=2))
        else:
            print(f"Panel 15 not found in {commit_hash}")
    except Exception as e:
        print(f"Error reading {commit_hash}: {e}")
