import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"C:/Users/franj/.gemini/antigravity/brain/f7e361f6-1b2a-4acb-abc7-8964d7af358f/.system_generated/steps/647/output.txt"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# The dashboard JSON from get_dashboard is wrapped in a dict with a "dashboard" key
db_json = data.get("dashboard", data)

for i, panel in enumerate(db_json.get("panels", [])):
    print(f"Panel ID={panel.get('id')} Title={panel.get('title')}")
    for target in panel.get("targets", []):
        sql = target.get("rawSql", "")
        # Print the last few lines or where clause
        where_lines = [line.strip() for line in sql.split("\n") if "WHERE" in line or "timeFilter" in line]
        print(f"  SQL where/filter: {where_lines}")
    print("-" * 30)
