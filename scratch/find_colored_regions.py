import os
from PIL import Image

def find_regions(path, name):
    print(f"\n=== Regions in {name} ===")
    if not os.path.exists(path):
        print("File does not exist.")
        return
    img = Image.open(path)
    w, h = img.size
    
    # Let's map pixels
    # We want to identify contiguous regions of non-background colors.
    # Background color is around (24, 27, 31)
    bg_r, bg_g, bg_b = 24, 27, 31
    
    # We will group colors:
    # 1. Yellow/Amber: R > 180, G > 150, B < 100
    # 2. Red: R > 150, G < 100, B < 100
    # 3. Blue/Cyan (markup): B > 180, R < 100
    # 4. White/Light gray: R > 200, G > 200, B > 200
    
    yellows = []
    reds = []
    blues = []
    whites = []
    
    for y in range(h):
        for x in range(w):
            p = img.getpixel((x, y))
            r, g, b = p[:3]
            if r > 180 and g > 150 and b < 100:
                yellows.append((x, y, p))
            elif r > 150 and g < 100 and b < 100:
                reds.append((x, y, p))
            elif b > 180 and r < 100:
                blues.append((x, y, p))
            elif r > 200 and g > 200 and b > 200:
                whites.append((x, y, p))
                
    for color_name, pixels in [("Yellow/Amber", yellows), ("Red", reds), ("Blue", blues), ("White", whites)]:
        if pixels:
            min_x = min(p[0] for p in pixels)
            max_x = max(p[0] for p in pixels)
            min_y = min(p[1] for p in pixels)
            max_y = max(p[1] for p in pixels)
            print(f"Color: {color_name}")
            print(f"  Count: {len(pixels)} pixels")
            print(f"  Bounding Box: X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")
            
find_regions("artifacts/media1.png", "media1.png")
find_regions("artifacts/media2.png", "media2.png")
