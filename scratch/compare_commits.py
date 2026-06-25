import subprocess

cmd = 'git show dbdcbaf -- grafana/provisioning/dashboards/plan_dashboard.json'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
lines = res.stdout.split('\n')

for i, line in enumerate(lines):
    if '"id": 5' in line or '"id": 10' in line or 'rawSql' in line:
        start = max(0, i - 10)
        end = min(len(lines), i + 20)
        print(f"=== Line {i} ===")
        print("\n".join(lines[start:end]))
