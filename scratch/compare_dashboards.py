import json
import sys

def analyze_dashboard(path, out):
    out.write(f"\n=================== {path} ===================\n")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for p in data.get("panels", []):
        out.write(f"Panel ID: {p.get('id')} | Title: '{p.get('title')}' | Type: '{p.get('type')}'\n")
        for idx, t in enumerate(p.get("targets", [])):
            sql = t.get("rawSql") or t.get("expr") or ""
            out.write(f"  Target {idx} (Ref: {t.get('refId')}):\n")
            out.write(f"    SQL:\n{sql}\n")
            out.write("-" * 40 + "\n")

with open("scratch/dashboards_info.txt", "w", encoding="utf-8") as out:
    analyze_dashboard("grafana/provisioning/dashboards/turno_actual_dashboard.json", out)
    analyze_dashboard("grafana/provisioning/dashboards/plan_dashboard.json", out)

print("Wrote output to scratch/dashboards_info.txt")
