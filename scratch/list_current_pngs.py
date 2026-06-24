import os
import glob

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain\78cca2d3-c973-422e-983a-9f20ec0fd824"
files = glob.glob(os.path.join(brain_dir, "**", "*.png"), recursive=True)
files.sort(key=os.path.getmtime)

print("=== PNG FILES ===")
for f in files:
    size = os.path.getsize(f)
    print(f"{f} | Size: {size} bytes")
