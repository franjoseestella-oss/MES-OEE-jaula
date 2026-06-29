import os
from PIL import Image

def image_to_ascii(img_path, txt_path, start_x, end_x):
    if not os.path.exists(img_path):
        return
    img = Image.open(img_path).convert("L") # grayscale
    w, h = img.size
    
    # Downsample slightly to make it readable in a text file
    # Let's say we scale height to 35 rows and width proportionally
    scale_y = 0.5
    scale_x = 0.25 # characters are taller than they are wide, so we compress width more
    
    new_h = int(h * scale_y)
    new_w = int((end_x - start_x) * scale_x)
    
    cropped = img.crop((start_x, 0, end_x, h))
    resized = cropped.resize((new_w, new_h))
    
    chars = " .:-=+*#%@"
    # Or simple black & white:
    # We want text (which is white/light on dark background) to be visible.
    
    lines = []
    for y in range(new_h):
        line = ""
        for x in range(new_w):
            val = resized.getpixel((x, y))
            # val is 0-255. 0 is black, 255 is white.
            # Map higher value (lighter) to denser char or block
            char_idx = int(val / 256 * len(chars))
            line += chars[char_idx]
        lines.append(line)
        
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written ASCII art to {txt_path}")

# Let's do it for the whole width but focused on regions, e.g., X=0 to 1024
image_to_ascii("artifacts/media1.png", "scratch/media1_ascii.txt", 0, 1024)
image_to_ascii("artifacts/media2.png", "scratch/media2_ascii.txt", 0, 1024)

# Also let's do a high-resolution one for the blue bounding box area (X=500 to 700)
image_to_ascii("artifacts/media1.png", "scratch/media1_blue_zone.txt", 500, 700)
image_to_ascii("artifacts/media2.png", "scratch/media2_blue_zone.txt", 500, 700)
