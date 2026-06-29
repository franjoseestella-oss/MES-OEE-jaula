import os
import json

dir_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards"

for f in os.listdir(dir_path):
    if f.endswith('.json'):
        full_path = os.path.join(dir_path, f)
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                print(f"File: {f}")
                print(f"  UID:   {data.get('uid')}")
                print(f"  Title: {data.get('title')}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
