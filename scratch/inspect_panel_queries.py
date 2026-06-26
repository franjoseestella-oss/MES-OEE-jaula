import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    data = json.load(f)

panels = data.get("panels", [])
for p in panels:
    pid = p.get("id")
    title = p.get("title", "")
    if pid in [5, 10]:
        targets = p.get("targets", [])
        for idx, t in enumerate(targets):
            raw_sql = t.get("rawSql", "")
            ref_id = t.get("refId", "")
            filename = f"scratch/panel_{pid}_{ref_id}.sql"
            with open(filename, "w", encoding="utf-8") as out:
                out.write(raw_sql)
            print(f"Extracted Panel {pid} ({title}) query {ref_id} to {filename}")
