import json

log_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"
with open(log_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        print(line[:300])
        if i > 5:
            break
