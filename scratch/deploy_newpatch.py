"""Deploy the new patched JS to the Grafana container and update the manifest."""
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

NEW_FILENAME = "5017.aaaa340b86e350c74a1f.js"
OLD_FILENAME = "5017.aaaa340b86e350c74a1e.js"
BUILD_PATH = "/usr/share/grafana/public/build"

# 1. Copy the new patched file into the container
print("Step 1: Copying new patched JS to container...")
result = subprocess.run(
    ['docker', 'cp', f'scratch/5017_newpatch.js', f'mes_grafana:{BUILD_PATH}/{NEW_FILENAME}'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"  cp result: {result.returncode} {result.stderr[:100]}")

# 2. Read the assets-manifest.json from the container
print("\nStep 2: Reading assets-manifest.json...")
result2 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'cat', f'{BUILD_PATH}/assets-manifest.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
manifest = json.loads(result2.stdout)
print(f"  Manifest has {len(manifest)} entries")

# 3. Update the manifest entry for 5017
old_entry = manifest.get(OLD_FILENAME)
if old_entry:
    # Create new entry with new filename, remove integrity (it won't match)
    new_entry = {
        'src': f'public/build/{NEW_FILENAME}',
        'integrity': ''
    }
    manifest[NEW_FILENAME] = new_entry
    # Keep old entry too, but also update it to point to new file
    # Actually, let's also replace any references within values
    for key in list(manifest.keys()):
        val = manifest[key]
        if isinstance(val, dict) and val.get('src', '').find(OLD_FILENAME) >= 0:
            manifest[key]['src'] = val['src'].replace(OLD_FILENAME, NEW_FILENAME)
            manifest[key]['integrity'] = ''
            print(f"  Updated: {key}")
        elif isinstance(val, str) and OLD_FILENAME in val:
            manifest[key] = val.replace(OLD_FILENAME, NEW_FILENAME)
            print(f"  Updated string: {key}")
    print(f"  New entry added: {NEW_FILENAME}")
else:
    print(f"  WARNING: '{OLD_FILENAME}' not found as a key, updating all string values...")
    for key in list(manifest.keys()):
        val = manifest[key]
        if isinstance(val, dict):
            src = val.get('src', '')
            if OLD_FILENAME in src:
                manifest[key]['src'] = src.replace(OLD_FILENAME, NEW_FILENAME)
                manifest[key]['integrity'] = ''
                print(f"  Updated dict key: {key}")

# 4. Write updated manifest to local temp file
print("\nStep 3: Writing manifest to local temp file...")
new_manifest_str = json.dumps(manifest, separators=(',', ':'))
with open('scratch/assets-manifest-new.json', 'w', encoding='utf-8') as f:
    f.write(new_manifest_str)
print(f"  Written {len(new_manifest_str):,} chars to scratch/assets-manifest-new.json")

# 5. Copy manifest to container
print("\nStep 4: Copying manifest to container...")
result3 = subprocess.run(
    ['docker', 'cp', 'scratch/assets-manifest-new.json', 
     f'mes_grafana:{BUILD_PATH}/assets-manifest.json'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"  cp result: {result3.returncode} {result3.stderr[:100]}")

# 6. Verify
result4 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'sh', '-c', 
     f"grep -c '{NEW_FILENAME}' {BUILD_PATH}/assets-manifest.json"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"\nStep 5: Verify - new filename occurrences in manifest: {result4.stdout.strip()}")

result5 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'ls', '-la', f'{BUILD_PATH}/{NEW_FILENAME}'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"New file in container:\n  {result5.stdout.strip()}")

print("\nDone! Hard-refresh your browser (Ctrl+Shift+R) to pick up the new JS.")
