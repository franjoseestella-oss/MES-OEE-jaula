import json

with open("scratch/plan_dashboard_8am.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data.get("panels", []):
    if p.get("id") == 10:
        print("Panel Type:", p.get("type"))
        print("\n--- options ---")
        print(json.dumps(p.get("options", {}), indent=2, ensure_ascii=False))
        print("\n--- fieldConfig ---")
        print(json.dumps(p.get("fieldConfig", {}), indent=2, ensure_ascii=False))
