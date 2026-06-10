import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    dashboard = json.load(f)

def print_panels(panels, indent=""):
    for p in panels:
        print(f"{indent}ID: {p.get('id')}, Title: {p.get('title')}, Type: {p.get('type')}")
        if "panels" in p:
            print_panels(p["panels"], indent + "  ")

print_panels(dashboard.get("panels", ""))
