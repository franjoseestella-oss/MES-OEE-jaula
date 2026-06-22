import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2\.system_generated\logs\overview.txt"

if not os.path.exists(log_path):
    print("Log file not found.")
    sys.exit(0)

print("Reading log...")
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Print lines that look like user messages or show tool calls related to dashboards or sql
for i, line in enumerate(lines):
    # If it contains user messages or key keywords
    if any(k in line.lower() for k in ["user", "prompt", "message", "dashboard", "timeline", "secuencia", "panel"]):
        # print line index and content (truncated to 200 chars)
        print(f"{i}: {line.strip()[:200]}")
