import json

with open("scratch/diff/mes-oee-v1_live.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for idx, panel in enumerate(db.get("panels", [])):
    print(f"Index {idx} | ID: {panel.get('id')} | Title: '{panel.get('title')}' | Type: {panel.get('type')}")
    if panel.get("targets"):
        for t in panel.get("targets"):
            print(f"  Target: {t.get('rawSql')}")
