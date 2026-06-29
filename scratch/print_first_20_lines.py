import os

log_path = r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e\.system_generated\logs\overview.txt"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for i in range(20):
            line = f.readline()
            if not line:
                break
            print(f"Line {i}: {line[:150]}")
else:
    print("Not found")
