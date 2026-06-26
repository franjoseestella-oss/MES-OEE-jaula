import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
# Let's find the latest .resolved files under C:\Users\franj\.gemini\antigravity\brain\ff73665e-0611-4498-9577-e0ed64617210\browser
browser_dir = r"C:\Users\franj\.gemini\antigravity\brain\ff73665e-0611-4498-9577-e0ed64617210\browser"
if os.path.exists(browser_dir):
    files = [f for f in os.listdir(browser_dir) if "scratchpad_r99zl8g8.md.resolved" in f]
    # Sort files naturally
    files.sort(key=lambda x: [int(s) if s.isdigit() else s for s in x.split('.')])
    if files:
        latest_file = files[-1]
        print(f"Reading: {latest_file}")
        with open(os.path.join(browser_dir, latest_file), 'r', encoding='utf-8', errors='ignore') as f:
            print(f.read())
    else:
        print("No files matched pattern")
else:
    print("Browser directory does not exist")













