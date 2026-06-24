import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_git_file(filepath):
    return subprocess.check_output(["git", "show", "HEAD:" + filepath]).decode("utf-8")

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"

with open(filepath, "r", encoding="utf-8") as f:
    current = json.load(f)

original = json.loads(get_git_file(filepath))

# Compare panel queries
for orig_p in original.get("panels", []):
    pid = orig_p.get("id")
    curr_p = next((p for p in current.get("panels", []) if p.get("id") == pid), None)
    if not curr_p:
        print(f"Panel {pid} removed!")
        continue
        
    orig_sql = orig_p.get("targets", [{}])[0].get("rawSql")
    curr_sql = curr_p.get("targets", [{}])[0].get("rawSql")
    
    if orig_sql != curr_sql:
        print(f"\n=== Query changed for Panel {pid} ({orig_p.get('title')}) ===")
        print("ORIGINAL:")
        print(orig_sql)
        print("CURRENT:")
        print(curr_sql)
        
    orig_def = orig_p.get("fieldConfig", {}).get("defaults", {})
    curr_def = curr_p.get("fieldConfig", {}).get("defaults", {})
    if orig_def != curr_def:
        print(f"\n=== Defaults changed for Panel {pid} ({orig_p.get('title')}) ===")
        print("ORIGINAL:")
        print(json.dumps(orig_def, indent=2, ensure_ascii=False))
        print("CURRENT:")
        print(json.dumps(curr_def, indent=2, ensure_ascii=False))
