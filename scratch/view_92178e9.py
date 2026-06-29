import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    diff = subprocess.check_output(
        ["git", "show", "92178e9", "--", "grafana/provisioning/dashboards/plan_dashboard.json"],
        stderr=subprocess.STDOUT
    ).decode("utf-8", errors="replace")
    
    # Let's filter lines of interest or write the diff to a utf-8 file so we can view it
    with open("scratch/diff_92178e9.txt", "w", encoding="utf-8") as f:
        f.write(diff)
    print("Wrote diff of 92178e9 to scratch/diff_92178e9.txt")
except Exception as e:
    print("Error:", e)
