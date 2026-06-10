import json

with open("grafana/provisioning/dashboards/log_dashboard.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Find all occurrences of keys related to color, background, custom styles, cellOptions
color_keys = set()
for p in db.get("panels", []):
    # let's look for "color" in nested dicts
    def recurse(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                if "color" in k.lower() or "mode" in k.lower():
                    print(f"Panel {p.get('id')} ({p.get('title')}): {path}.{k} = {v}")
                recurse(v, f"{path}.{k}")
        elif isinstance(d, list):
            for i, x in enumerate(d):
                recurse(x, f"{path}[{i}]")
    recurse(p)
