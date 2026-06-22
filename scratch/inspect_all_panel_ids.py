import json

with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for p in db.get("panels", []):
    targets = p.get("targets", [])
    if not targets:
        continue
    print(f"=== Panel {p.get('id')}: {p.get('title')} (Targets: {len(targets)}) ===")
    for idx, t in enumerate(targets):
        print(f"  Target {idx} ({t.get('refId')}):")
        sql = t.get("rawSql", "")
        # print first 3 lines and last 3 lines
        lines = sql.split("\n")
        if len(lines) <= 6:
            print("\n".join(f"    {l}" for l in lines))
        else:
            print("\n".join(f"    {l}" for l in lines[:3]))
            print("    ...")
            print("\n".join(f"    {l}" for l in lines[-3:]))
    print()
