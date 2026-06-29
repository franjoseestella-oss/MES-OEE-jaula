import json
import sys

file_path = r"grafana/provisioning/dashboards/plan_dashboard.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

panels = data.get("panels", [])
for p in panels:
    if p.get("id") == 10:
        with open("scratch/panel_10_details.txt", "w", encoding="utf-8") as out:
            out.write("Panel Title: " + str(p.get("title")) + "\n")
            out.write("\n--- fieldConfig ---\n")
            out.write(json.dumps(p.get("fieldConfig", {}), indent=2, ensure_ascii=False))
            out.write("\n\n--- options ---\n")
            out.write(json.dumps(p.get("options", {}), indent=2, ensure_ascii=False))
            out.write("\n\n--- targets ---\n")
            out.write(json.dumps(p.get("targets", []), indent=2, ensure_ascii=False))
        print("Written to scratch/panel_10_details.txt")
        break
