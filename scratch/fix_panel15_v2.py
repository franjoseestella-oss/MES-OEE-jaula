"""
Fix panel 15 gauge config AND force apply to container.
Since OneDrive keeps reverting the file, we:
1. Read the current file
2. Fix panel 15 in memory
3. Write to local file
4. Immediately docker cp to container
5. Delete and recreate grafana volume
6. Start grafana fresh
"""
import json
import subprocess
import time

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
print(f"  handler keys: {[m.get('handlerKey') for t in panel_15.get('transformations',[]) for m in t.get('options',{}).get('mappings',[])]}")

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
print(f"  handler keys: {[m.get('handlerKey') for t in panel_15.get('transformations',[]) for m in t.get('options',{}).get('mappings',[])]}")

# Write the fixed version to a SCRATCH location (not OneDrive)
SCRATCH_PATH = r"scratch\log_dashboard_fixed.json"
with open(SCRATCH_PATH, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"\nFixed file written to {SCRATCH_PATH}")

# Also write to the main path
with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"Also written to {FILE_PATH}")

# Verify the scratch file
with open(SCRATCH_PATH, "r", encoding="utf-8") as f:
    verify = json.load(f)
p15 = [x for x in verify["panels"] if x.get("id") == 15][0]
print(f"\nVERIFY scratch file: min={p15['fieldConfig']['defaults']['min']}, max={p15['fieldConfig']['defaults']['max']}")
