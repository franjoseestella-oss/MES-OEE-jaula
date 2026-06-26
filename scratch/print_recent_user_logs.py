import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\cbf08d14-19ca-4311-8710-0b0653a29a18\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print("Log file not found.")
    sys.exit(0)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"--- Printing last 150 lines of overview.txt ({len(lines)} total lines) ---")
for line in lines[-150:]:
    print(line, end="")

