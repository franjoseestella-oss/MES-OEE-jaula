import json
import sys

# Ensure UTF-8 output on standard output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

step392_path = r"C:\Users\franj\.gemini\antigravity\brain\1caa288f-f0b3-4fb0-ac6f-9226b5d92d9f\.system_generated\steps\392\output.txt"

with open(step392_path, "r", encoding="utf-8") as f:
    data = json.load(f)

db = data.get("dashboard", data)
print(f"Title: {db.get('title')}")
print(f"Panels: {len(db.get('panels', []))}")
for p in db.get("panels", []):
    title = p.get('title', '').encode('utf-8', errors='ignore').decode('utf-8')
    print(f"- ID {p.get('id')}: {title} ({p.get('type')})")
