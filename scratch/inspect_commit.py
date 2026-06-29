import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/git_history_plan_dashboard.txt", "r", encoding="utf-8") as f:
    content = f.read()

import re
commits = re.split(r"(^commit [a-f0-9]+)", content, flags=re.MULTILINE)

target_commit = "464c4907a0da446607ea2a6767576bbacdcdc4b9"
for i in range(1, len(commits), 2):
    if target_commit in commits[i]:
        print(commits[i])
        # Print first 2000 chars of the body
        print(commits[i+1][:5000])
        break
else:
    print("Commit not found")
