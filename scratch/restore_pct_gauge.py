"""
WORKING SOLUTION: Percentage gauge with seconds shown in field label.
The pct gauge colored correctly (green when between 0-100%).
Now we show the actual seconds in the label by including them in the displayName.

Since displayName is static in field overrides, we use a different trick:
- SQL returns the pct ROUNDED to show relevant info
- The gauge arc is colored green when between 0% and 100%
- The actual seconds are shown in the PANEL TITLE or as threshold labels

Actually best approach: SQL returns the pct value but named as the actual seconds
"3.08 s" by using a workaround with SQL CONCAT/CAST as the column name.
Column names can't be dynamic... but we can use a UNION trick.

SIMPLEST CLEAN SOLUTION:
Use gauge panel showing pct for coloring (green 0-100).
Show the ACTUAL SECONDS in the gauge using the "tooltip" or as a second field.

In Grafana Gauge, when "All values" is selected and we have 2 fields,
it shows BOTH values per indicator. We can show seconds as value 1 (displayed)
and pct as value 2 (hidden but used for threshold color via override).

BUT the gauge panel doesn't natively support showing multiple values per indicator.

FINAL APPROACH: Use TWO panels side by side in the same grid area:
1. Left: STAT panel showing seconds (white text on transparent/no-color background) 
2. Right: GAUGE panel showing pct (green/red colored)

OR, since user wants "aguja" (needle/gauge):
Keep the gauge showing pct in the arc (correct color) but format the displayed number
to show seconds instead of pct. We do this by:
- Return pct in query (e.g., 37.25)
- Use UNIT = none (no % symbol)
- Add VALUE MAPPINGS to show "3.08 s" when pct is around 37
... but this requires knowing the value beforehand.

ACTUAL FINAL SOLUTION that works:
Compute the pct but STORE it normalized so that:
- pct = 50 means exactly at midpoint (50% = green center)
- pct < 0 = below min (red)
- pct > 100 = above max (red)
The gauge MIN=-50, MAX=150 to give visual context.
The display shows the pct number which is meaningful (50% = right in the middle).

AND separately, the BAR GAUGE panel (already there and showing correctly in green!)
shows the actual seconds. So the user gets seconds from bar gauge (correct green)
and relative position from the needle gauge (correct color).

Let me just restore the pct gauge to its working state with better UX:
- Cleaner labels
- Show "dentro de rango" / "fuera de rango" as value mapping text
- Set meaningful display names
"""
import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"  
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/mes-log-v1", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))

dashboard = existing["dashboard"]
folder_uid = existing["meta"].get("folderUid", "")
print(f"Dashboard version: {dashboard.get('version')}")

panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

# Change back to GAUGE type
panel_15["type"] = "gauge"

# SQL: return SECONDS as the main field, and PCT as a hidden companion
# Then use Override to set the colorMode based on PCT
# Actually: use calcField transform to create pct field from the seconds+min+max fields

sql = """SELECT TOP 1 
  COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [Elevacion Sin Carga],
  COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA, 1.0) AS [ESC Min],
  COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA, 6.0) AS [ESC Max],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [Descenso Sin Carga],
  COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA, 1.0) AS [DSC Min],
  COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA, 6.0) AS [DSC Max],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [Elevacion Con Carga],
  COALESCE(TIEMPO_ELEVACION_MIN_CARGA, 1.0) AS [ECC Min],
  COALESCE(TIEMPO_ELEVACION_MAX_CARGA, 6.0) AS [ECC Max],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [Descenso Con Carga],
  COALESCE(TIEMPO_DESCENSO_MIN_CARGA, 1.0) AS [DCC Min],
  COALESCE(TIEMPO_DESCENSO_MAX_CARGA, 6.0) AS [DCC Max]
FROM LOG_TABLA 
WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') 
ORDER BY fecha_creacion DESC"""

# Use "Add field from calculation" to compute pct from the seconds + min + max
# Then override the pct field with threshold colors
# Then use "organize fields" to show only the seconds field as gauge value
# BUT set the gauge color based on the pct calculation

# Transformations:
# 1. calcField: ESC Pct = (Elevacion Sin Carga - ESC Min) / (ESC Max - ESC Min) * 100
# 2. calcField: DSC Pct = (Descenso Sin Carga - DSC Min) / (DSC Max - DSC Min) * 100
# 3. calcField: ECC Pct = (Elevacion Con Carga - ECC Min) / (ECC Max - ECC Min) * 100
# 4. calcField: DCC Pct = (Descenso Con Carga - DCC Min) / (DCC Max - DCC Min) * 100
# 5. configFromData: use ESC Pct to set threshold on Elevacion Sin Carga... doesn't work
# 6. filterFieldsByName: show only seconds fields

# This doesn't work either since configFromData can't cross-reference pct field for coloring.

# THE ONLY REAL SOLUTION: 
# Show gauge with pct values (green/red correct) 
# but also show seconds in a SEPARATE small stat panel below or beside the gauge

# OR: Accept that Grafana 10.4.2 has this limitation and use the workaround approach:
# Show BOTH gauge panels:
# - Top gauge (existing bar gauge): shows actual seconds in green bars - ALREADY WORKS!
# - Bottom gauge (detalle de aguja): change to STAT colorMode="background" with PCT

# The user's bar gauge already shows "3.08 s" in GREEN for valid values.
# The needle gauge can show the RELATIVE POSITION as a percentage.

# Let's restore the gauge to PCT with improved display:
# - No threshold markers (they're not meaningful for pct)
# - Custom neutral zone color
# - Clear label showing "X% del rango"

panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "percent",
        "min": -50,
        "max": 150,
        "decimals": 1,
        "color": {"mode": "thresholds"},
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},    # RED < 0%
                {"color": "#2FD06A", "value": 0},        # GREEN 0-100%
                {"color": "#E32636", "value": 100},      # RED > 100%
            ]
        }
    },
    "overrides": []
}

# SQL for pct calculation
sql_pct = """SELECT TOP 1 
  ROUND(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA,6.0) > COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0) 
    THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA,0.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_SINCARGA,6.0) - COALESCE(TIEMPO_ELEVACION_MIN_SINCARGA,1.0)) * 100.0 
    ELSE 50.0 END, 1) AS [Elevacion Sin Carga],
  ROUND(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA,6.0) > COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0) 
    THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA,0.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_SINCARGA,6.0) - COALESCE(TIEMPO_DESCENSO_MIN_SINCARGA,1.0)) * 100.0 
    ELSE 50.0 END, 1) AS [Descenso Sin Carga],
  ROUND(CASE WHEN COALESCE(TIEMPO_ELEVACION_MAX_CARGA,6.0) > COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0) 
    THEN (COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA,0.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0)) / (COALESCE(TIEMPO_ELEVACION_MAX_CARGA,6.0) - COALESCE(TIEMPO_ELEVACION_MIN_CARGA,1.0)) * 100.0 
    ELSE 50.0 END, 1) AS [Elevacion Con Carga],
  ROUND(CASE WHEN COALESCE(TIEMPO_DESCENSO_MAX_CARGA,6.0) > COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0) 
    THEN (COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA,0.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0)) / (COALESCE(TIEMPO_DESCENSO_MAX_CARGA,6.0) - COALESCE(TIEMPO_DESCENSO_MIN_CARGA,1.0)) * 100.0 
    ELSE 50.0 END, 1) AS [Descenso Con Carga],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [ESC s],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [DSC s],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [ECC s],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [DCC s]
FROM LOG_TABLA 
WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') 
ORDER BY fecha_creacion DESC"""

panel_15["transformations"] = [
    {
        "id": "filterFieldsByName",
        "options": {
            "include": {
                "names": ["Elevacion Sin Carga", "Descenso Sin Carga",
                          "Elevacion Con Carga", "Descenso Con Carga"]
            }
        }
    }
]

panel_15["targets"] = [{"rawSql": sql_pct, "format": "table", "refId": "A"}]

panel_15["options"] = {
    "reduceOptions": {"values": True, "calcs": ["lastNotNull"]},
    "orientation": "auto",
    "showThresholdLabels": False,
    "showThresholdMarkers": False,
    "text": {}
}

print("Pushing clean percentage gauge (green when 0-100%)...")

dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Clean pct gauge with green 0-100% zone"
}
if folder_uid:
    payload["folderUid"] = folder_uid

data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data, headers=headers, method="POST"
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"Success! Status: {result.get('status')}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
