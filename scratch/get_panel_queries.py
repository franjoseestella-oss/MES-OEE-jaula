import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

print("Panels in plan_dashboard.json:")
print("=" * 80)
for panel in dashboard.get("panels", []):
    panel_id = panel.get("id")
    title = panel.get("title")
    print(f"Panel ID: {panel_id} | Title: {title}")
    
    # If it's a row, check subpanels
    for target in panel.get("targets", []):
        sql = target.get("sql", {}).get("rawSql") or target.get("rawSql")
        if sql:
            print(f"--- Query (RefId: {target.get('refId')}):")
            print(sql)
            print("-" * 40)
            
    for subpanel in panel.get("panels", []):
        sub_id = subpanel.get("id")
        sub_title = subpanel.get("title")
        print(f"  Sub-Panel ID: {sub_id} | Title: {sub_title}")
        for target in subpanel.get("targets", []):
            sql = target.get("sql", {}).get("rawSql") or target.get("rawSql")
            if sql:
                print(f"    --- Query (RefId: {target.get('refId')}):")
                print(sql)
                print("    " + "-" * 36)
print("=" * 80)
