"""
Show the full threshold1 and threshold2 handler area in the JS patch.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

js_path = r'scratch\5017.aaaa340b86e350c74a1f.js'
with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find threshold1 key
marker = 'key:"threshold1"'
idx = content.find(marker)
if idx == -1:
    marker = 'key:\"threshold1\"'
    idx = content.find(marker)
if idx == -1:
    # Try without quotes type
    idx = content.find('threshold1')
    print(f"Using fallback search at {idx}")

print(f"Found at {idx}")
# Show 3000 chars from there
snippet = content[idx-200 : idx+3000]
print(repr(snippet))
