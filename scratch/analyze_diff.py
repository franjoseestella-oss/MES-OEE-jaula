import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/plan_dashboard_diff.txt", "r", encoding="utf-16") as f:
    diff_content = f.read()

print(diff_content[:5000]) # Print first 5000 characters
