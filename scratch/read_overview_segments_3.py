import os
import sys
import json

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
folder = "e568e209-e1ec-4288-a6ca-6cc1d24b942c"
log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")

with open(log_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

line_294 = lines[293]
data = json.loads(line_294)
print("Content of L294:")
print(data.get("content"))
