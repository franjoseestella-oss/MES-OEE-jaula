import os
import json

path = r"C:\Users\franj\.gemini\antigravity\browser_recordings\e1630d34-9f7f-44dc-8a18-8dfc6494f30c"
metadata_file = os.path.join(path, "metadata.json")
if os.path.exists(metadata_file):
    print("=== metadata.json ===")
    with open(metadata_file, "r") as f:
        print(f.read())
else:
    print("metadata.json not found")

print("All files in recording directory:")
for root, dirs, files in os.walk(path):
    for f in files:
        print(os.path.relpath(os.path.join(root, f), path))
