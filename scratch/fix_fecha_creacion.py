import json
import re

# 1. Update plan_dashboard.json
print("Updating plan_dashboard.json...")
with open("grafana/provisioning/dashboards/plan_dashboard.json", "r", encoding="utf-8") as f:
    content = f.read()

# Replace fecha_creacion with FECHA_HORA_INICIO_SEC appropriately
content = content.replace("CAST(fecha_creacion AS DATE)", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATE)")
content = content.replace("log.fecha_creacion", "TRY_CAST(log.FECHA_HORA_INICIO_SEC AS DATETIME2)")
content = content.replace("fecha_creacion >= @ShiftStart", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStart")
content = content.replace("fecha_creacion <= @EvalTime", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTime")
content = content.replace("fecha_creacion >= @ShiftStartActive", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) >= @ShiftStartActive")
content = content.replace("fecha_creacion <= @EvalTimeActive", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) <= @EvalTimeActive")
content = content.replace("fecha_creacion AS time", "TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2) AS time")
content = content.replace("ORDER BY fecha_creacion", "ORDER BY TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2)")

with open("grafana/provisioning/dashboards/plan_dashboard.json", "w", encoding="utf-8") as f:
    f.write(content)
print("plan_dashboard.json updated successfully!")

# 2. Update distribuidor_dashboard.json
print("Updating distribuidor_dashboard.json...")
with open("grafana/provisioning/dashboards/distribuidor_dashboard.json", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("$__timeFilter(fecha_creacion)", "$__timeFilter(TRY_CAST(FECHA_HORA_INICIO_SEC AS DATETIME2))")
content = content.replace("ORDER BY fecha_creacion DESC", "ORDER BY id DESC")

with open("grafana/provisioning/dashboards/distribuidor_dashboard.json", "w", encoding="utf-8") as f:
    f.write(content)
print("distribuidor_dashboard.json updated successfully!")

# 3. Update scripts/get_latest_data.py
print("Updating scripts/get_latest_data.py...")
with open("scripts/get_latest_data.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "fecha_creacion DESC" in line:
        line = line.replace("fecha_creacion DESC", "id DESC")
    new_lines.append(line)

with open("scripts/get_latest_data.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("scripts/get_latest_data.py updated successfully!")
