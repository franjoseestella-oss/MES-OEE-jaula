"""Check assets-manifest.json in the container."""
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Copy from container
r = subprocess.run(
    ['docker', 'cp',
     'mes_grafana:/usr/share/grafana/public/build/assets-manifest.json',
     'scratch/assets-manifest-current.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("copy result:", r.returncode, r.stderr[:100])

with open('scratch/assets-manifest-current.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

keys = list(manifest.keys())
print("Top-level keys:", keys[:10])

# Check entrypoints
ep = manifest.get('entrypoints', {})
app = ep.get('app', {})
print("app entrypoint keys:", list(app.keys()))

assets = app.get('assets', {})
js_files = assets.get('js', [])
print(f"JS files count: {len(js_files)}")

# Find 5017 reference
for f in js_files:
    if '5017' in f:
        print(f"5017 in entrypoints: {f}")

# Also check direct keys
for k,v in manifest.items():
    if '5017' in str(v):
        print(f"5017 found in key '{k}'")
        break
