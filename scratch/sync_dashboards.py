import json
import glob
import os

# Standard 5 links
standard_links = [
  {
    "asDropdown": False,
    "icon": "home",
    "includeVars": False,
    "keepTime": False,
    "tags": [],
    "targetBlank": False,
    "title": "Inicio",
    "type": "link",
    "url": "/d/mes-home-v1"
  },
  {
    "asDropdown": False,
    "icon": "dashboard",
    "includeVars": True,
    "keepTime": True,
    "tags": [],
    "targetBlank": False,
    "title": "OEE/MES",
    "type": "link",
    "url": "/d/panel-oee-mes-fabrica"
  },
  {
    "asDropdown": False,
    "icon": "dashboard",
    "includeVars": False,
    "keepTime": False,
    "tags": [],
    "targetBlank": False,
    "title": "DISTRIBUIDOR",
    "type": "link",
    "url": "/d/mes-oee-v2"
  },
  {
    "asDropdown": False,
    "icon": "dashboard",
    "includeVars": True,
    "keepTime": True,
    "tags": [],
    "targetBlank": False,
    "title": "LOG_SECUENCIAS",
    "type": "link",
    "url": "/d/mes-reg-v1"
  },
  {
    "asDropdown": False,
    "icon": "alert",
    "includeVars": True,
    "keepTime": True,
    "tags": [],
    "targetBlank": False,
    "title": "ALARMAS",
    "type": "link",
    "url": "/d/mes-alarms-v1"
  }
]

# 1. Restore & Modify distribuidor_dashboard.json from scratch/backup_dashboards/oee_dashboard.json
print("Restoring and modifying distribuidor_dashboard.json...")
backup_path = "scratch/backup_dashboards/oee_dashboard.json"
dest_path = "grafana/provisioning/dashboards/distribuidor_dashboard.json"

with open(backup_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

db["uid"] = "mes-oee-v2"
db["title"] = "LOGISNEXT — DISTRIBUIDOR"
db["links"] = standard_links

with open(dest_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("Saved distribuidor_dashboard.json.")

# 2. Modify alarmas_dashboard.json
print("Updating alarmas_dashboard.json...")
alarmas_path = "grafana/provisioning/dashboards/alarmas_dashboard.json"
with open(alarmas_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
db["links"] = standard_links
with open(alarmas_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# 3. Modify registro_dashboard.json
print("Updating registro_dashboard.json...")
registro_path = "grafana/provisioning/dashboards/registro_dashboard.json"
with open(registro_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
db["links"] = standard_links

# Recursively replace URLs in overrides or panels
def update_links_in_json(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and "/d/mes-log-v1?var-selected_id=" in v:
                new_v = v.replace("/d/mes-log-v1?var-selected_id=", "/d/mes-oee-v2?var-selected_id=")
                print(f"Replacing url: {v} -> {new_v}")
                obj[k] = new_v
            else:
                update_links_in_json(v)
    elif isinstance(obj, list):
        for item in obj:
            update_links_in_json(item)

update_links_in_json(db)

with open(registro_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# 4. Modify turno_actual_dashboard.json
print("Updating turno_actual_dashboard.json...")
turno_path = "grafana/provisioning/dashboards/turno_actual_dashboard.json"
with open(turno_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
db["links"] = standard_links
with open(turno_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("All dashboards sync'ed locally!")
