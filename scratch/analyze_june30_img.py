import os
from PIL import Image

path = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\media__1782821527853.png"
if os.path.exists(path):
    img = Image.open(path)
    print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
    # Let's count unique colors
    w, h = img.size
    colors = img.getcolors(w * h)
    if colors:
        print(f"Unique colors: {len(colors)}")
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
        print("Top 15 colors:")
        for count, rgba in sorted_colors[:15]:
            print(f"  {rgba}: {count} pixels ({count/(w*h)*100:.2f}%)")
else:
    print("File not found")
