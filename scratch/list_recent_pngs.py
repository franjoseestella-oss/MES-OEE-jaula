import os
import glob

media_dir = r"C:\Users\franj\.gemini\antigravity\brain\9ddfdb95-2f21-4ff6-ae75-1d9ff0ae28e3\.tempmediaStorage"
files = glob.glob(os.path.join(media_dir, "*"))
files.sort(key=os.path.getmtime)

print("=== MEDIA STORAGE FILES (Oldest to Newest) ===")
for f in files:
    size = os.path.getsize(f)
    mtime = os.path.getmtime(f)
    print(f"{os.path.basename(f)} | Size: {size} bytes | Mtime: {mtime}")
