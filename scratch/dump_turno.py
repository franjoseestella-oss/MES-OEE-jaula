import json

with open("grafana/provisioning/dashboards/turno_actual_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

with open("scratch/turno_details.txt", "w", encoding="utf-8") as out:
    for p in db.get("panels", []):
        out.write(f"=== Panel {p.get('id')}: {p.get('title')} ===\n")
        out.write(json.dumps(p, indent=2, ensure_ascii=False) + "\n\n")
print("Done writing to scratch/turno_details.txt")
