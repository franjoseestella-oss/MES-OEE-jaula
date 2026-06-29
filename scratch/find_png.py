import os
import glob

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774"

print("Searching for images in current conversation directory:")
for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"]:
    files = glob.glob(os.path.join(brain_dir, "**", ext), recursive=True)
    for f in files:
        print(f)


