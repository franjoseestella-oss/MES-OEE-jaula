import json
import glob
import os

files = glob.glob(r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\*.json")

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            title = data.get("title", "No Title")
            vars_list = data.get("templating", {}).get("list", [])
            print(f"\nDashboard: {os.path.basename(file_path)} ({title})")
            if vars_list:
                for v in vars_list:
                    print(f"  Variable: {v.get('name')} | Type: {v.get('type')} | Query: {v.get('query')}")
            else:
                print("  No variables")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
