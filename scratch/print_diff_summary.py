import json

def get_panels_info(db):
    return [(p.get("id"), p.get("title"), p.get("type")) for p in db.get("panels", [])]

with open("scratch/diff/mes-oee-v1_local.json", "r", encoding="utf-8") as f:
    local_db = json.load(f)
    
with open("scratch/diff/mes-oee-v1_live.json", "r", encoding="utf-8") as f:
    live_db = json.load(f)

local_panels = get_panels_info(local_db)
live_panels = get_panels_info(live_db)

print("Local Panels count:", len(local_panels))
for p in local_panels:
    print("  Local:", p)

print("Live Panels count:", len(live_panels))
for p in live_panels:
    print("  Live:", p)
