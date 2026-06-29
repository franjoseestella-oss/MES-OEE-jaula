from PIL import Image
import os

img_path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\media__1782729162431.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    print(f"Format: {img.format}")
    print(f"Size: {img.size}")
    print(f"Mode: {img.mode}")
    # Let's save a copy to the scratch folder or print colors if it's very small
    print("Image loaded successfully.")
else:
    print("Image not found.")
