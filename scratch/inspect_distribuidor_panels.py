import json
import os

dashboard_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

target_ids = [102, 104, 106, 111, 113, 115]
for panel in dashboard.get("panels", []):
    pid = panel.get("id")
    if pid in target_ids or not target_ids:
        print(f"Panel ID: {pid}, Title: {panel.get('title')}, Type: {panel.get('type')}")
        if "fieldConfig" in panel:
            defaults = panel["fieldConfig"].get("defaults", {})
            print(f"  Min/Max: {defaults.get('min')}/{defaults.get('max')}")
            print(f"  Thresholds: {defaults.get('thresholds')}")
        print("-" * 50)
