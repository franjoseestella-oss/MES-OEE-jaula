"""Fix the entrypoints in the manifest to use the new JS filename."""
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

OLD_FILENAME = "5017.aaaa340b86e350c74a1e.js"
NEW_FILENAME = "5017.aaaa340b86e350c74a1f.js"
BUILD_PATH = "/usr/share/grafana/public/build"

result = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'cat', f'{BUILD_PATH}/assets-manifest.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
manifest = json.loads(result.stdout)

# Fix the entrypoints entry - it has the JS list for the app
entrypoints = manifest.get('entrypoints', {})
for ep_name, ep_data in entrypoints.items():
    assets = ep_data.get('assets', {})
    js_list = assets.get('js', [])
    new_js_list = [j.replace(OLD_FILENAME, NEW_FILENAME) for j in js_list]
    if js_list != new_js_list:
        print(f"Updating entrypoint '{ep_name}' JS list:")
        for old, new in zip(js_list, new_js_list):
            if old != new:
                print(f"  {old} -> {new}")
        assets['js'] = new_js_list

# Also update the top-level 5017 key (already done, but verify)
if OLD_FILENAME in manifest:
    manifest[OLD_FILENAME]['src'] = manifest[OLD_FILENAME]['src'].replace(OLD_FILENAME, NEW_FILENAME)

# Write back
print("\nWriting updated manifest...")
new_manifest_str = json.dumps(manifest, separators=(',', ':'))
with open('scratch/assets-manifest-new2.json', 'w', encoding='utf-8') as f:
    f.write(new_manifest_str)

result2 = subprocess.run(
    ['docker', 'cp', 'scratch/assets-manifest-new2.json', 
     f'mes_grafana:{BUILD_PATH}/assets-manifest.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"Copy result: {result2.returncode} {result2.stderr[:100]}")

# Verify entrypoints
result3 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'cat', f'{BUILD_PATH}/assets-manifest.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
manifest2 = json.loads(result3.stdout)
print("\nVerification - entrypoints 'app' JS list:")
for js in manifest2.get('entrypoints', {}).get('app', {}).get('assets', {}).get('js', []):
    print(f"  {js}")

old_count = result3.stdout.count(OLD_FILENAME)
new_count = result3.stdout.count(NEW_FILENAME)
print(f"\nOld filename occurrences: {old_count}")
print(f"New filename occurrences: {new_count}")

print("\nAll done! Hard-refresh browser (Ctrl+Shift+R) now.")
