import os
import sys

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"

# Let's search all logs for "teorica" or "anterior" or similar terms to see what changes were made in past conversations.
for folder in os.listdir(brain_dir):
    log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            text = f.read()
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if any(x in line for x in ["teorica", "teórica", "out_of_order", "anterior a la", "no quietes"]):
                if "USER" in line or "MODEL" in line:
                    print(f"[{folder}] Line {idx+1}: {line[:200]}")
