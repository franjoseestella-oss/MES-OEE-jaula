import subprocess
import re

def main():
    diff = subprocess.check_output(['git', 'diff', 'grafana/provisioning/dashboards/plan_dashboard.json']).decode('utf-8', errors='ignore')
    lines = diff.split('\n')
    
    # We want to identify the panel structure. The plan_dashboard.json has panels.
    # Let's read the current file and find where panel titles are located in the file lines.
    with open('grafana/provisioning/dashboards/plan_dashboard.json', 'r', encoding='utf-8') as f:
        local_content = f.read()
    
    # We can parse the diff chunk by chunk to see what changed and in which panels.
    # A standard unified diff has chunks starting with @@.
    # Let's print out the diff lines that start with + or - and some surrounding context.
    print("Diff summary of modifications in plan_dashboard.json:")
    
    # Let's run a simple regex search to see what is added or removed
    # or just print lines starting with + or - that are not meta (+++, ---, @@, diff)
    hunks = diff.split('@@')
    for hunk in hunks:
        if not hunk.strip():
            continue
        # Find if this hunk mentions a title
        titles = re.findall(r'"title":\s*"([^"]+)"', hunk)
        # Find if it is about a panel
        added = [l for l in hunk.split('\n') if l.startswith('+') and not l.startswith('+++')]
        removed = [l for l in hunk.split('\n') if l.startswith('-') and not l.startswith('---')]
        
        if added or removed:
            print("-" * 50)
            if titles:
                print(f"Hunk mentioning titles: {titles}")
            else:
                print("Hunk (no title found in hunk itself)")
            print(f"Added lines: {len(added)}, Removed lines: {len(removed)}")
            print("First 3 added:")
            for l in added[:3]:
                print(f"  {l[:150]}")
            print("First 3 removed:")
            for l in removed[:3]:
                print(f"  {l[:150]}")

if __name__ == '__main__':
    main()
