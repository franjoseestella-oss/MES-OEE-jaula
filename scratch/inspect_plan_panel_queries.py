import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("C:/Users/franj/.gemini/antigravity/brain/ff73665e-0611-4498-9577-e0ed64617210/.system_generated/steps/1308/output.txt", "r", encoding="utf-8") as f:
    data = json.load(f)

dashboard = data.get("dashboard", {})
panels = dashboard.get("panels", [])

panels_to_inspect = {4, 5, 10}

for p in panels:
    pid = p.get('id')
    if pid in panels_to_inspect:
        print(f"\n========================================================================\nPANEL ID: {pid} | Title: {p.get('title')}\n========================================================================\n")
        targets = p.get('targets', [])
        for t in targets:
            ref_id = t.get('refId')
            query = t.get('rawSql') or t.get('expr') or t.get('query')
            print(f"--- Target refId: {ref_id} ---")
            print(query)
            print()
