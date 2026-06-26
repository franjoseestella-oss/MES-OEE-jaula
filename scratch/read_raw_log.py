import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\5e6fce02-1734-4391-8a88-93b57b1083a0\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i in range(10):
            line = f.readline()
            print(f"Line {i}: {repr(line)}")
else:
    print("Not found")
