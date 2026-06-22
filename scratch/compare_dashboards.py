import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

local_path = "grafana/provisioning/dashboards/plan_dashboard.json"
live_path = r"C:\Users\franj\.gemini\antigravity\brain\1caa288f-f0b3-4fb0-ac6f-9226b5d92d9f\.system_generated\steps\392\output.txt"

with open(local_path, "r", encoding="utf-8") as f:
    local_db = json.load(f)

with open(live_path, "r", encoding="utf-8") as f:
    live_db = json.load(f)
    if "dashboard" in live_db:
        live_db = live_db["dashboard"]

for pid in [9, 10]:
    local_panel = next((p for p in local_db.get("panels", []) if p.get("id") == pid), None)
    live_panel = next((p for p in live_db.get("panels", []) if p.get("id") == pid), None)
    
    print(f"\n=================== PANEL {pid} COMPARISON ===================")
    if not local_panel:
        print("Local panel: NOT FOUND")
    if not live_panel:
        print("Live panel: NOT FOUND")
        continue
    
    if local_panel and live_panel:
        # Compare title, type, transformations, options, targets count
        print(f"Titles: Local='{local_panel.get('title')}', Live='{live_panel.get('title')}'")
        print(f"Types: Local='{local_panel.get('type')}', Live='{live_panel.get('type')}'")
        print(f"Options match? {local_panel.get('options') == live_panel.get('options')}")
        if local_panel.get('options') != live_panel.get('options'):
            print("  Local options:", json.dumps(local_panel.get('options'), indent=2))
            print("  Live options:", json.dumps(live_panel.get('options'), indent=2))
            
        print(f"Transformations match? {local_panel.get('transformations') == live_panel.get('transformations')}")
        if local_panel.get('transformations') != live_panel.get('transformations'):
            print("  Local transformations:", json.dumps(local_panel.get('transformations'), indent=2))
            print("  Live transformations:", json.dumps(live_panel.get('transformations'), indent=2))
            
        print(f"Targets count: Local={len(local_panel.get('targets', []))}, Live={len(live_panel.get('targets', []))}")
        
        # Compare SQL queries
        local_sql = local_panel.get('targets', [{}])[0].get('rawSql', '')
        live_sql = live_panel.get('targets', [{}])[0].get('rawSql', '')
        print(f"SQL queries match? {local_sql == live_sql}")
        if local_sql != live_sql:
            print("--- LOCAL SQL (first 500 chars) ---")
            print(local_sql[:500])
            print("--- LIVE SQL (first 500 chars) ---")
            print(live_sql[:500])
