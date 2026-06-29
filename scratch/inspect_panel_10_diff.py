import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Run git diff for plan_dashboard.json
cmd = ["git", "diff", "HEAD", "--", "grafana/provisioning/dashboards/plan_dashboard.json"]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

lines = result.stdout.splitlines()
in_panel_10 = False
in_raw_sql = False
panel_10_id_found = False

# We can search the diff output. Since we want to find the diff of Panel 10 SQL:
# In the JSON, the panel has "id": 10.
# Let's inspect where in the diff the changes are.
# Let's write all lines starting with "+" or "-" that are SQL queries of panel 10.
# Let's just parse the full diff and search for the block containing "id": 10 or Panel 10 title.
# Let's output all diff lines to help us understand.
with open("scratch/inspect_panel_10_diff_output.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print("Diff output written to scratch/inspect_panel_10_diff_output.txt")

# Let's write a parser to find if it is panel 10
# A simple way: find the hunks and check if "id": 10 or "title": "Plan de Producción..." is nearby
# Let's read the file we just wrote and search for the context.
with open("scratch/inspect_panel_10_diff_output.txt", "r", encoding="utf-8") as f:
    diff_lines = f.readlines()

hunks = []
current_hunk = []
for line in diff_lines:
    if line.startswith("@@"):
        if current_hunk:
            hunks.append(current_hunk)
        current_hunk = [line]
    elif line.startswith("diff --git"):
        if current_hunk:
            hunks.append(current_hunk)
        current_hunk = []
    elif current_hunk:
        current_hunk.append(line)
if current_hunk:
    hunks.append(current_hunk)

print(f"Total hunks: {len(hunks)}")
for idx, hunk in enumerate(hunks):
    hunk_text = "".join(hunk)
    # Check if this hunk is part of panel 10
    # Panel 10 has id 10. Let's see if we see 10 or "Plan de Producción" or states like "Esperando" in it
    if "Plan de" in hunk_text or '"id": 10' in hunk_text or "Esperando" in hunk_text or "AlarmIntervals" in hunk_text:
        print(f"\n--- Hunk {idx+1} ---")
        # Print lines that are added or removed
        for l in hunk:
            if l.startswith("+") or l.startswith("-"):
                if not (l.startswith("+++") or l.startswith("---")):
                    # print first 150 chars
                    print(l.strip()[:150])
