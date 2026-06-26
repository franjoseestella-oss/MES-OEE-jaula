import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
if os.path.exists(brain_dir):
    print("Available brain directories:")
    for d in os.listdir(brain_dir):
        print(d)
else:
    print("Brain directory does not exist")

