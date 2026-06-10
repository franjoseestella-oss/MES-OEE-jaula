import json

with open("scratch/assets-manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

for k, v in manifest.items():
    if "aaaa340b86e350c74a1e" in str(v) or "5017" in str(k):
        print(f"Key: {k} -> Value: {v}")
