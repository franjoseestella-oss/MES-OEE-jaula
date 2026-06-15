import os
import json

dashboards_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards"

for filename in os.listdir(dashboards_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(dashboards_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"=== {filename} (Title: {data.get('title')}) ===")
                links = data.get("links", [])
                for link in links:
                    print(f"  - Link Title: {link.get('title')} | URL: {link.get('url')} | keepTime: {link.get('keepTime')} | includeVars: {link.get('includeVars')}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
