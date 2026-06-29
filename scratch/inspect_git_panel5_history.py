import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Run git log and extract the commits affecting plan_dashboard.json
try:
    commits = subprocess.check_output(
        ["git", "log", "--format=%H %s", "grafana/provisioning/dashboards/plan_dashboard.json"],
        stderr=subprocess.STDOUT
    ).decode("utf-8", errors="replace").strip().split("\n")
    
    for c_line in commits[:15]:
        commit_hash, commit_msg = c_line.split(" ", 1)
        # Get the file content at this commit
        try:
            content = subprocess.check_output(
                ["git", "show", f"{commit_hash}:grafana/provisioning/dashboards/plan_dashboard.json"],
                stderr=subprocess.STDOUT
            ).decode("utf-8", errors="replace")
            
            db = json.loads(content)
            for p in db.get("panels", []):
                if p.get("id") == 5:
                    sql = p.get("targets", [{}])[0].get("rawSql", "")
                    if "Alarma" in sql or "alarma" in sql:
                        print(f"Commit {commit_hash[:8]} ({commit_msg}) HAS ALARMA IN PANEL 5:")
                        # Print the CASE statement for Estado
                        lines = sql.split("\n")
                        for i, line in enumerate(lines):
                            if "AS [Estado]" in line or "AS Estado" in line:
                                # Print surrounding lines
                                start = max(0, i - 10)
                                end = min(len(lines), i + 2)
                                print("\n".join(lines[start:end]))
                                print("-" * 40)
        except Exception as e:
            pass
except Exception as e:
    print(f"Error: {e}")
