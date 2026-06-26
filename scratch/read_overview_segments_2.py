import os
import sys
import json

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
folder = "a961276b-cf64-4f02-b78b-201b21659b4e"
log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")

with open(log_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

line_487 = lines[486]
data = json.loads(line_487)
print(data.get("content"))
