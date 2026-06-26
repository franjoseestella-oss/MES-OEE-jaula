import json

def inspect_dashboard(filepath):
    print(f"\n========================================\nINSPECTING: {filepath}\n========================================")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Check panels
    panels = data.get("panels", [])
    for p in panels:
        print(f"Panel ID: {p.get('id')} | Title: '{p.get('title')}' | Type: '{p.get('type')}'")
        targets = p.get("targets", [])
        for i, t in enumerate(targets):
            print(f"  Target {i} (RefId: {t.get('refId')}):")
            sql = t.get("rawSql", "")
            # print first few lines of SQL
            lines = sql.strip().split("\n")
            print("    SQL (truncated):")
            for line in lines[:10]:
                print(f"      {line}")
            if len(lines) > 10:
                print(f"      ... ({len(lines) - 10} more lines)")

inspect_dashboard("grafana/provisioning/dashboards/turno_actual_dashboard.json")
inspect_dashboard("grafana/provisioning/dashboards/plan_dashboard.json")
