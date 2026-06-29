import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/git_history_plan_dashboard.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Let's split the git log by commits
commits = re.split(r"(^commit [a-f0-9]+)", content, flags=re.MULTILINE)
print(f"Total commit parts: {len(commits)}")

# Find any mentions of "color", "mapping", "NOK", "OK" in the commits
for i in range(1, len(commits), 2):
    commit_header = commits[i]
    commit_body = commits[i+1] if (i+1) < len(commits) else ""
    
    # Check if there is a color change
    if "color" in commit_body or "mapping" in commit_body or "OK_NOK" in commit_body:
        print(f"\n--- Commit: {commit_header.strip()} ---")
        lines = commit_body.splitlines()
        for idx, line in enumerate(lines):
            # Print subject of commit (usually first few lines)
            if idx < 10:
                print(line)
            # Print lines of interest
            elif any(k in line for k in ["color", "mapping", "NOK", "OK", "yellow", "red", "green", "Esperando"]):
                if line.strip().startswith("-") or line.strip().startswith("+"):
                    print(f"Line {idx}: {line}")
