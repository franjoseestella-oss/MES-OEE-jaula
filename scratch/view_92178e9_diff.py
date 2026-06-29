import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    # Get the diff for commit 92178e9 matching plan_dashboard.json
    diff = subprocess.check_output(
        ["git", "show", "92178e9", "--", "grafana/provisioning/dashboards/plan_dashboard.json"],
        stderr=subprocess.STDOUT
    ).decode("utf-8", errors="replace")
    
    lines = diff.split("\n")
    for i, line in enumerate(lines):
        if "Alarma" in line:
            print(f"Line {i}: {line}")
            # Print surrounding lines
            start = max(0, i - 15)
            end = min(len(lines), i + 15)
            print("\n".join(lines[start:end]))
            print("=" * 60)
except Exception as e:
    print(f"Error: {e}")
