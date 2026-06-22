import json

filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
try:
    with open(filepath, "r", encoding="utf-8") as f:
        db = json.load(f)
except Exception as e:
    db = {}

panels = {p.get("id"): p for p in db.get("panels", [])}

output = []
for pid in [9, 10]:
    p = panels.get(pid)
    if p:
        output.append(f"# Panel {pid}: {p.get('title')}\n")
        output.append(f"- **Type**: {p.get('type')}\n")
        output.append(f"- **GridPos**: {p.get('gridPos')}\n")
        targets = p.get("targets", [])
        output.append(f"- **Targets count**: {len(targets)}\n")
        for idx, t in enumerate(targets):
            output.append(f"## Target {idx} (RefId: {t.get('refId')}):\n")
            output.append(f"**Format**: {t.get('format')}\n")
            output.append("### SQL:\n")
            output.append("```sql\n" + str(t.get('rawSql')) + "\n```\n")
        output.append("## Options:\n")
        output.append("```json\n" + json.dumps(p.get("options", {}), indent=2) + "\n```\n")
        output.append("-" * 80 + "\n")
    else:
        output.append(f"# Panel {pid} not found\n")

with open("scratch/panel_details.md", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Created scratch/panel_details.md successfully.")
