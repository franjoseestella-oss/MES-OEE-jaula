with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '"id": 4' in line:
        print(f"id 4 at line {idx+1}: {line.strip()}")
    if '"id": 10' in line:
        print(f"id 10 at line {idx+1}: {line.strip()}")
