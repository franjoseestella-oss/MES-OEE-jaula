"""
Find the configFromData handler registry in the Grafana JS bundle.
Looking for the 'threshold1' and 'threshold2' handler keys.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

js_path = r'scratch\5017.aaaa340b86e350c74a1f.js'
print(f"Reading {js_path}...")
with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"Total chars: {len(content):,}")

# Search for handler registry keywords
keywords = ['handlerKey', 'handlerRegistry', 'configFromData', '"threshold1"', "'threshold1'"]
for kw in keywords:
    idx = 0
    count = 0
    while True:
        idx = content.find(kw, idx)
        if idx == -1 or count > 3:
            break
        snippet = content[max(0,idx-50):idx+200]
        print(f"\n--- '{kw}' at {idx} ---")
        print(repr(snippet[:300]))
        idx += 1
        count += 1
