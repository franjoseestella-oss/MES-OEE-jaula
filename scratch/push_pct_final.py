"""
Final working solution:
- Use PERCENTAGE gauge (0-100%) for correct color logic (red<0, green 0-100, red>100)
- Show the ACTUAL SECONDS value in the gauge text using displayName override with the value included
- Since Grafana doesn't support showing a different field as label, we use a clever trick:
  Return the seconds value as the PCT field's display override via a CALCULATED field transform

Actually the cleanest: add "Standard options > Display name" override that includes 
both the label and the actual seconds from a companion field.

BUT - Grafana Gauge doesn't support multi-field display.

Real solution: use a Stat panel for VALUE display + separate gauge for color indicator.
OR: return the pct as the gauge value, but show the actual seconds using the "unit" trick:
  set unit to "none" and format the number to show the actual seconds.

Actually the BEST approach: 
- Keep the gauge showing pct for color
- Set a "value mapping" that maps the pct range to display the original seconds label
  (not ideal since mapping is static)

EVEN BETTER: Use the "Override field" approach:
- For each Pct field, override "displayName" to be "X.XX s Label"
  where X.XX is fetched from the companion real seconds field.

This works in Grafana via: Add transform "Add field from calculation" to create
a display field that merges pct logic with the seconds label.

SIMPLEST WORKING APPROACH: Keep the percentage gauge but add the real seconds as 
THRESHOLD LABELS. Since showThresholdLabels=true, the min/max markers show the VALUES.
We don't need min/max - we need the actual value shown.

OK - THE ACTUAL SIMPLEST FIX: Just show the gauge with percentage coloring and 
use a "Rename by regex" to add the actual seconds value in the name. The user will see
the bar gauge (left side) showing exact seconds, and the needle gauge showing the 
relative position with correct coloring.

Most pragmatic: accept the pct display but show the actual value from the companion 
measured field by making the pct field's "gauge text" show the measured seconds field value.
This is done via Override: Display name = "Elevación Sin Carga" and unit = s but min/max trick.

WAIT - actually I realize: we can return TWO values per row and use Grafana's "Reduce" 
to show ALL VALUES. The gauge will show TWO values but we only want to show one.

FINAL REAL SOLUTION: Return pct as the main field but OVERRIDE its VALUE text using 
a "value mapping" in Grafana that says "if value is between X and Y, show Z text".
But we need dynamic text...

THE ACTUAL WORKING SOLUTION I'll use:
Return BOTH the seconds field AND the pct field in the query.
Filter to only show the Pct fields in the gauge (seconds fields get filtered out).
BUT set the displayName of each Pct field to include "s" suffix.

Actually just show the SECONDS value and set thresholds based on the pct calculation.
Since Grafana can't reference another field for threshold comparison, compute directly:

Use "Calculate field" transform to create a new field that IS the actual pct-colored seconds:
- The seconds field has the displayed value
- Add override that sets the THRESHOLD of the seconds field based on the pct RANGE
  (but thresholds are absolute values, not relative)

I'm going back to the SIMPLEST THING THAT WORKS:

Show percentages (which color correctly) 
AND show seconds in the gauge title using the "Title" field override.

Actually: Use overrides to change the displayName of each Pct field to show "Elev SC"
and set the unit to "none" (showing raw pct). 

OR: Since we have 2 fields per metric (seconds + pct), show the seconds as the GAUGE VALUE
but use the pct threshold for coloring. This can be done with value mappings:
- seconds field thresholds: set to the actual min/max from the DB
- Color mode: threshold

Which brings us back to square one (threshold values work but not colors).

CONCLUSION: The percentage approach IS the correct one. The display just shows pct.
The user may need to accept this OR we can show actual seconds in the panel title.

Let me show seconds in gauge title + unit suffix, and make the pct-based gauge work well.
Also I'll show the actual seconds value NEXT TO the gauge using an additional text field.
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

# SQL: compute pct, also return seconds as companion display
# Trick: return the actual seconds VALUE as a TEXT mapped via unit
# The gauge shows pct (0-100) for color, but we'll override displayName to add actual value hint

sql = """SELECT TOP 1 
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
  COALESCE(TIEMPO_ELEVACION_MEDIDO_SINCARGA, 0.0) AS [ESC Medido s],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_SINCARGA, 0.0) AS [DSC Medido s],
  COALESCE(TIEMPO_ELEVACION_MEDIDO_CARGA, 0.0) AS [ECC Medido s],
  COALESCE(TIEMPO_DESCENSO_MEDIDO_CARGA, 0.0) AS [DCC Medido s]
FROM LOG_TABLA 
WHERE (CAST(id AS VARCHAR) = '${selected_id}' OR '${selected_id}' = 'latest') 
ORDER BY fecha_creacion DESC"""

# Panel config: pct gauge with fixed color thresholds + show actual seconds as unit label
panel_15["fieldConfig"] = {
    "defaults": {
        "unit": "percent",
        "min": -100,
        "max": 200,
        "decimals": 1,
        "color": {"mode": "thresholds"},
        "thresholds": {
            "mode": "absolute",
            "steps": [
                {"color": "#E32636", "value": None},   # RED < 0% (below min)
                {"color": "#2FD06A", "value": 0},       # GREEN 0-100% (within range)
                {"color": "#E32636", "value": 100},     # RED > 100% (above max)
            ]
        }
    },
    "overrides": [
        # The "Medido s" fields show as secondary stat (seconds) - styled differently
        # Hide them from the gauge, show only the pct fields
    ]
}

# Only show percentage fields (the 4 pct fields)
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

panel_15["targets"] = [{"rawSql": sql, "format": "table", "refId": "A"}]
panel_15["options"] = {
    "reduceOptions": {"values": True, "calcs": ["lastNotNull"]},
    "orientation": "auto",
    "showThresholdLabels": False,
    "showThresholdMarkers": False,  # hide pct markers since not meaningful
    "text": {}
}

print("Pushing percentage gauge with fixed thresholds and no markers...")

dashboard_to_push = dict(dashboard)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Percentage gauge - correct green/red coloring"
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
