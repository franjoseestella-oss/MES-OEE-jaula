import os
import sys

# Ensure stdout handles unicode/utf-8 properly
if sys.platform.startswith('win'):
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
folder = "e568e209-e1ec-4288-a6ca-6cc1d24b942c"
log_file = os.path.join(brain_dir, folder, ".system_generated", "logs", "overview.txt")

with open(log_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

print("--- Segment around Line 294 ---")
for idx in range(max(0, 290 - 15), min(len(lines), 310 + 15)):
    print(f"L{idx+1}: {lines[idx][:250]}")

print("\n--- Segment around Line 407 ---")
for idx in range(max(0, 400 - 15), min(len(lines), 420 + 15)):
    print(f"L{idx+1}: {lines[idx][:250]}")
