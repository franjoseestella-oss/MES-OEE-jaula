"""
Fix panel 15 gauge config: min/max and thresholds.
This script reads the local JSON, modifies panel 15 in memory,
then writes it back, ALSO copies it directly into the Docker container.
"""
import json
import subprocess

FILE_PATH = r"grafana\provisioning\dashboards\log_dashboard.json"

# Read local file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

# Find panel 15
panel_15 = None
for p in dashboard["panels"]:
    if p.get("id") == 15:
        panel_15 = p
        break

if not panel_15:
    print("ERROR: Panel 15 not found!")
    exit(1)

print("BEFORE:")
print(f"  min: {panel_15['fieldConfig']['defaults']['min']}")
print(f"  max: {panel_15['fieldConfig']['defaults']['max']}")
print(f"  thresholds: {json.dumps(panel_15['fieldConfig']['defaults']['thresholds'])}")

# Fix min/max
panel_15["fieldConfig"]["defaults"]["min"] = 1
panel_15["fieldConfig"]["defaults"]["max"] = 6

# Fix thresholds: single red base step
panel_15["fieldConfig"]["defaults"]["thresholds"] = {
    "mode": "absolute",
    "steps": [
        {"color": "#E32636", "value": None}
    ]
}

# Fix all threshold2 -> threshold1 in transformations
for t in panel_15.get("transformations", []):
    if t.get("id") == "configFromData":
        for m in t["options"].get("mappings", []):
            if m.get("handlerKey") == "threshold2":
                m["handlerKey"] = "threshold1"

print("\nAFTER:")
print(f"  min: {panel_15['fieldConfig']['defaults']['min']}")
print(f"  max: {panel_15['fieldConfig']['defaults']['max']}")
print(f"  thresholds: {json.dumps(panel_15['fieldConfig']['defaults']['thresholds'])}")

# Write back to file
with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"\nFile written to {FILE_PATH}")

# Also copy it into the Docker container
try:
    subprocess.run([
        "docker", "cp", FILE_PATH,
        "mes_grafana:/etc/grafana/provisioning/dashboards/log_dashboard.json"
    ], check=True)
    print("File copied into Docker container")
except Exception as e:
    print(f"Docker cp failed: {e}")

# Verify inside container
result = subprocess.run([
    "docker", "exec", "mes_grafana",
    "python3", "-c",
    "import json; d=json.load(open('/etc/grafana/provisioning/dashboards/log_dashboard.json')); p=[x for x in d['panels'] if x.get('id')==15][0]; print('Container min:', p['fieldConfig']['defaults']['min']); print('Container max:', p['fieldConfig']['defaults']['max'])"
], capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    # Try with grep
    result2 = subprocess.run([
        "docker", "exec", "mes_grafana",
        "grep", "-n", "min", "/etc/grafana/provisioning/dashboards/log_dashboard.json"
    ], capture_output=True, text=True)
    print("grep min in container:\n", result2.stdout[:300])
