import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for panel in data.get("panels", []):
    if panel.get("id") == 10:
        print("=== TITLE ===")
        print(panel.get("title"))
        print("\n=== TYPE ===")
        print(panel.get("type"))
        print("\n=== RAW SQL ===")
        print(panel.get("targets", [{}])[0].get("rawSql"))
        print("\n=== FIELD CONFIG OVERRIDES ===")
        print(json.dumps(panel.get("fieldConfig", {}).get("overrides", []), indent=2, ensure_ascii=False))
        print("\n=== PANEL OPTIONS ===")
        print(json.dumps(panel.get("options", {}), indent=2, ensure_ascii=False))
        break
