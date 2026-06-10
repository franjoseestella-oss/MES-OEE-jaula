"""Check if the runtime.js has 5017 chunk reference."""
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'sh', '-c',
     'grep -c 5017 /usr/share/grafana/public/build/runtime.fc87f4ca8fd62d3e0dc7.js'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("5017 count in runtime:", result.stdout.strip(), "stderr:", result.stderr.strip())

result2 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'wc', '-c',
     '/usr/share/grafana/public/build/runtime.fc87f4ca8fd62d3e0dc7.js'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("runtime.js size:", result2.stdout.strip())

# Copy runtime.js locally
result3 = subprocess.run(
    ['docker', 'cp',
     'mes_grafana:/usr/share/grafana/public/build/runtime.fc87f4ca8fd62d3e0dc7.js',
     'scratch/runtime.js'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("copy runtime:", result3.returncode)

with open('scratch/runtime.js', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"Runtime size: {len(content)}")
# Find 5017
if '5017' in content:
    idx = content.find('5017')
    print("5017 context:", repr(content[max(0,idx-100):idx+200]))
else:
    print("5017 NOT found in runtime.js")
    # Find what chunk hashes are there
    import re
    hashes = re.findall(r'[0-9a-f]{20}', content)
    print("Hashes found:", set(hashes)[:10])
