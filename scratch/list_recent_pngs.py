import glob
import os

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain\70912b51-1041-4be2-9d46-655465e25ab2"
png_files = glob.glob(os.path.join(brain_dir, "**", "*.png"), recursive=True)

# sort by modification time
png_files.sort(key=os.path.getmtime, reverse=True)

for f in png_files[:10]:
    print(f, os.path.getmtime(f))
