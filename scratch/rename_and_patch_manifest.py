import json
import os
import subprocess

# Read local manifest
manifest_path = "scratch/assets-manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest_content = f.read()

# Replace file names to change hash from aaaa340b86e350c74a1e to aaaa340b86e350c74a1f
new_manifest_content = manifest_content.replace(
    "5017.aaaa340b86e350c74a1e.js", "5017.aaaa340b86e350c74a1f.js"
).replace(
    "5017.aaaa340b86e350c74a1e.js.map", "5017.aaaa340b86e350c74a1f.js.map"
)

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(new_manifest_content)

# Rename the local patched JS file
if os.path.exists("scratch/5017.aaaa340b86e350c74a1e.js"):
    if os.path.exists("scratch/5017.aaaa340b86e350c74a1f.js"):
        os.remove("scratch/5017.aaaa340b86e350c74a1f.js")
    os.rename("scratch/5017.aaaa340b86e350c74a1e.js", "scratch/5017.aaaa340b86e350c74a1f.js")
    print("Renamed local JS file to *f.js")

# Copy the renamed JS file to container
subprocess.run([
    "docker", "cp", "scratch/5017.aaaa340b86e350c74a1f.js",
    "mes_grafana:/usr/share/grafana/public/build/5017.aaaa340b86e350c74a1f.js"
], check=True)

# Copy the modified manifest to container
subprocess.run([
    "docker", "cp", "scratch/assets-manifest.json",
    "mes_grafana:/usr/share/grafana/public/build/assets-manifest.json"
], check=True)

# Delete old file in container as root
subprocess.run([
    "docker", "exec", "-u", "root", "mes_grafana", "rm", "-f",
    "/usr/share/grafana/public/build/5017.aaaa340b86e350c74a1e.js"
], check=True)

print("Successfully updated container assets with the new hash name!")
