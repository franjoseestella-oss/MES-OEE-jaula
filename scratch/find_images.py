import os
import glob

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
image_paths = glob.glob(os.path.join(brain_dir, "**", "*.png"), recursive=True) + glob.glob(os.path.join(brain_dir, "**", "*.jpg"), recursive=True)

# Also check scratch/
scratch_images = glob.glob("scratch/*.png") + glob.glob("scratch/*.jpg")

print("Found brain images:")
for p in image_paths:
    print(f" - {p} (size: {os.path.getsize(p)} bytes)")

print("\nFound scratch images:")
for p in scratch_images:
    print(f" - {p} (size: {os.path.getsize(p)} bytes)")
