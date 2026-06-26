import json

def extract_queries():
    filepath = "grafana/provisioning/dashboards/plan_dashboard.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    panels = data.get("panels", [])
    for p in panels:
        pid = p.get("id")
        if pid in [5, 10]:
            title = p.get("title")
            targets = p.get("targets", [])
            if targets:
                sql = targets[0].get("rawSql", "")
                out_path = f"scratch/panel_{pid}_query.sql"
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(sql)
                print(f"Extracted Panel {pid} ('{title}') query to {out_path}")

if __name__ == "__main__":
    extract_queries()
