with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "227" in line:
        print(f"Line {i+1}: {line.strip()}")
        # print 5 lines before and after
        start = max(0, i - 5)
        end = min(len(lines), i + 6)
        for j in range(start, end):
            print(f"  {j+1}: {lines[j].strip()}")
        print("-" * 50)
