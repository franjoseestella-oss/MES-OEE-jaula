import os
from PIL import Image

def analyze_image(path, name):
    print(f"=== Analyzing {name} ({path}) ===")
    if not os.path.exists(path):
        print("File does not exist.")
        return
    img = Image.open(path)
    w, h = img.size
    print(f"Dimensions: {w}x{h}, Mode: {img.mode}")
    
    # Let's count colors
    colors = img.getcolors(w * h)
    if colors:
        print(f"Unique colors count: {len(colors)}")
        # Sort colors by frequency
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
        print("Top 10 colors by frequency:")
        for count, rgba in sorted_colors[:10]:
            print(f"  {rgba}: {count} pixels ({count/(w*h)*100:.1f}%)")
            
    # Find blue highlight: typically high B, lower R and G (e.g. b > 200, r < 100, g < 150)
    # Let's search for blue pixels
    blue_pixels = []
    for y in range(h):
        for x in range(w):
            pixel = img.getpixel((x, y))
            # support both RGB and RGBA
            r, g, b = pixel[:3]
            # blue color (like cyan/blue markup)
            if b > 180 and r < 100 and g < 180:
                blue_pixels.append((x, y, pixel))
    
    print(f"Detected {len(blue_pixels)} blue-ish pixels.")
    if blue_pixels:
        min_x = min(p[0] for p in blue_pixels)
        max_x = max(p[0] for p in blue_pixels)
        min_y = min(p[1] for p in blue_pixels)
        max_y = max(p[1] for p in blue_pixels)
        print(f"Blue bounding box: X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")

analyze_image("artifacts/media1.png", "media1.png")
analyze_image("artifacts/media2.png", "media2.png")
