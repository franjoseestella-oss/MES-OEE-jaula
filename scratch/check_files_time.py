import os
import time

files = [
    "scratch/plan_dashboard_8am.json",
    "grafana/provisioning/dashboards/plan_dashboard.json",
    "scratch/panel_10_A.sql",
    "scratch/panel_10_out_of_order_fix.sql",
    "scratch/restore_8am.py"
]

for f in files:
    if os.path.exists(f):
        mtime = os.path.getmtime(f)
        print(f"{f}: modified {time.ctime(mtime)} (size {os.path.getsize(f)} bytes)")
    else:
        print(f"{f}: NOT FOUND")
