import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
with open(filepath, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

for p in dashboard.get("panels", []):
    pid = p.get("id")
    title = p.get("title")
    print(f"\n=======================================================")
    print(f"PANEL ID: {pid} | Title: {title}")
    print(f"=======================================================")
    for t in p.get("targets", []):
        ref = t.get("refId")
        sql = t.get("rawSql") or t.get("expr") or t.get("query")
        print(f"--- Ref: {ref} ---")
        print(sql)
