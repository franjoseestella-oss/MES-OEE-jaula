import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/Users/franj/.gemini/antigravity/brain/ff73665e-0611-4498-9577-e0ed64617210/.system_generated/steps/1308/output.txt", "r", encoding="utf-8") as f:
    data = json.load(f)

dashboard = data.get("dashboard", {})
panels = dashboard.get("panels", [])

print(f"Dashboard Title: {dashboard.get('title')}")
for p in panels:
    pid = p.get('id')
    title = p.get('title')
    ptype = p.get('type')
    print(f"\n========================================\nPANEL ID: {pid} | Title: {title} | Type: {ptype}")
    targets = p.get('targets', [])
    for t in targets:
        ref_id = t.get('refId')
        query = t.get('rawSql') or t.get('expr') or t.get('query')
        print(f"  Target refId: {ref_id}")
        if query:
            # print first few lines of query
            lines = query.split('\n')
            for line in lines[:10]:
                print(f"    {line}")
            if len(lines) > 10:
                print(f"    ...")
