import os
import glob

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain\98665d5f-41bc-473e-83a7-d94f6dda62c7"
png_files = glob.glob(os.path.join(brain_dir, "**", "*.png"), recursive=True)
print("PNG FILES:")
for f in png_files:
    print(f)
