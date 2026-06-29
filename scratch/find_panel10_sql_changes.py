import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Get list of commit hashes for plan_dashboard.json
cmd = ["git", "log", "--format=%H", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
hashes = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()

print(f"Total commits to scan: {len(hashes)}")

for commit_hash in hashes:
    # Run git show
    cmd_show = ["git", "show", commit_hash, "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
    diff_output = subprocess.run(cmd_show, capture_output=True, text=True, encoding="utf-8").stdout
    
    # Check if this diff contains modifications to the SQL query of Panel 10
    # Panel 10 has title "Plan de Producción por Secuencias (Teórico vs Real)"
    # We can detect if the SQL of Panel 10 is changed by checking if "rawSql" changes are inside panel 10 or check if there's any SQL diff with "Esperando" or similar.
    # Let's count how many times "rawSql" is added or removed, or if we can see the commit message
    cmd_msg = ["git", "log", "--format=%B", "-n", "1", commit_hash]
    commit_msg = subprocess.run(cmd_msg, capture_output=True, text=True, encoding="utf-8").stdout.strip()
    
    # Let's check if the diff has + or - lines inside rawSql that mention states or conditions
    lines = diff_output.splitlines()
    panel10_modified = False
    for line in lines:
        if (line.startswith("+") or line.startswith("-")) and not (line.startswith("+++") or line.startswith("---")):
            if any(term in line for term in ["Esperando", "Alarma", "Exceso", "En proceso", "actual_start", "planned_start", "AlarmIntervals"]):
                # Make sure it's part of SQL query change
                if any(sql_term in line for sql_term in ["WHEN", "THEN", "AND", "OR", "SELECT", "ELSE", "EXISTS"]):
                    panel10_modified = True
                    break
                    
    if panel10_modified:
        print(f"\n==================================================")
        print(f"COMMIT: {commit_hash} | {commit_msg}")
        print(f"==================================================")
        # Let's print the SQL changes for this commit (lines containing WHEN or THEN or SELECT or Esperando)
        for line in lines:
            if (line.startswith("+") or line.startswith("-")) and not (line.startswith("+++") or line.startswith("---")):
                if any(term in line for term in ["Esperando", "Alarma", "Exceso", "En proceso", "actual_start", "planned_start", "AlarmIntervals"]):
                    print(line.strip())
