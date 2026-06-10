import subprocess

# Run git show on the commit
out = subprocess.check_output(['git', 'show', 'dc98fb2', '--', 'grafana/provisioning/dashboards/log_dashboard.json']).decode('utf-8', errors='ignore')

# Find panel 15 diff
idx = out.find('"id": 15')
if idx != -1:
    print("Found panel 15 in diff:")
    # Print 2000 characters before and after
    print(out[max(0, idx - 1000) : min(len(out), idx + 2500)])
else:
    print("Panel 15 not found in diff.")
