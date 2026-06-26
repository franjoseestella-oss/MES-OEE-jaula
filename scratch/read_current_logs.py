import os
import sys

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
folder = "e568e209-e1ec-4288-a6ca-6cc1d24b942c"

log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        text = f.read()
    # Let's find lines with these words
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if any(x in line for x in ["completada", "en proceso", "REFERENCIA_EN_CICLO", "eje", "eje vertical", "eje horizontal"]):
            if "USER" in line or "MODEL" in line:
                print(f"Line {idx+1}: {line[:200]}")
