import os
import glob

app_data = r"C:\Users\franj\AppData\Local\Temp" # or C:\Users\franj\.gemini\antigravity
print("Listing C:\\Users\\franj\\.gemini\\antigravity:")
for root, dirs, files in os.walk(r"C:\Users\franj\.gemini\antigravity"):
    for file in files:
        path = os.path.join(root, file)
        # print only files modified in the last 5 minutes
        import time
        if time.time() - os.path.getmtime(path) < 300:
            print(f"File: {path}, Size: {os.path.getsize(path)}, Age: {time.time() - os.path.getmtime(path):.1f}s")
