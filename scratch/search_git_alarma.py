import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Run git log to find all commits matching plan_dashboard.json and show their diffs for "Alarma"
try:
    output = subprocess.check_output(
        ["git", "log", "-p", "-G", "Alarma", "grafana/provisioning/dashboards/plan_dashboard.json"],
        stderr=subprocess.STDOUT
    ).decode("utf-8", errors="replace")
    print(output[:5000])  # Print first 5000 characters
except Exception as e:
    print(f"Error running git log: {e}")
