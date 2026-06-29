import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

commits = [f"HEAD~{i}" for i in range(15)]

for c in commits:
    try:
        content = subprocess.check_output(
            ["git", "show", f"{c}:grafana/provisioning/dashboards/plan_dashboard.json"],
            stderr=subprocess.STDOUT
        ).decode("utf-8", errors="replace")
        
        db = json.loads(content)
        print(f"=== Commit {c[:8]} ===")
        for p in db.get("panels", []):
            mappings = p.get("fieldConfig", {}).get("defaults", {}).get("mappings", [])
            for m in mappings:
                opts = m.get("options", {})
                for k, v in opts.items():
                    if "Alarma" in k or "alarma" in k:
                        print(f"  Panel ID {p.get('id')} ({p.get('title')}): Mapping '{k}' -> {v}")
    except Exception as e:
        print(f"Error for commit {c[:8]}: {e}")
