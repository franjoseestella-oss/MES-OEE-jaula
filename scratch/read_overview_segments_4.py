import os
import sys
import json
import re

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
for folder in os.listdir(brain_dir):
    log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r'"content":"([^"]*secuencia[^"]*)"', content, re.IGNORECASE)
        if matches:
            print(f"--- Folder {folder} ---")
            for m in matches[:10]:
                print(m[:150])
