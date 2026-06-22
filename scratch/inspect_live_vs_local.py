import json
import os
import sys

live_db_path = r"C:\Users\franj\.gemini\antigravity\brain\1caa288f-f0b3-4fb0-ac6f-9226b5d92d9f\.system_generated\steps\392\output.txt"

with open(live_db_path, "r", encoding="utf-8") as f:
    response = json.load(f)
    db = response.get("dashboard", response)

panels = db.get("panels", [])
for p in panels:
    pid = p.get("id")
    if pid in [9, 10]:
        print(f"=== Live Panel {pid}: '{p.get('title')}' ===")
        print(f"Type: {p.get('type')}")
        print(f"GridPos: {p.get('gridPos')}")
        print("Options:")
        print(json.dumps(p.get("options"), indent=2))
        print("Transformations:")
        print(json.dumps(p.get("transformations"), indent=2))
        targets = p.get("targets", [])
        print(f"Targets count: {len(targets)}")
        for idx, t in enumerate(targets):
            sql = t.get('rawSql', '')
            print(f"  Target {idx} (refId {t.get('refId')}): SQL len {len(sql)}")
        print("="*40)
