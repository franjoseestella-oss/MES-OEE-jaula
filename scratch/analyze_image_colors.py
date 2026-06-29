import shutil
import os
from PIL import Image

src = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\media__1782731464213.png"
dst = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\media__1782731464213.png"

try:
    shutil.copy2(src, dst)
    print("Copied successfully.")
except Exception as e:
    print(f"Error copying: {e}")

if os.path.exists(dst):
    img = Image.open(dst)
    w, h = img.size
    # Print vertical slices or average color per X coordinate
    # to identify color blocks.
    blocks = []
    current_color = None
    color_start = 0
    
    for x in range(w):
        # Sample middle row of pixels
        r, g, b, a = img.getpixel((x, h // 2))
        
        # Classify color roughly
        # Yellow: high R, high G, low B
        # Green: low R, high G, low B
        # Red: high R, low G, low B
        # Grey/Dark: low R, low G, low B
        if r > 180 and g > 180 and b < 100:
            color = "YELLOW"
        elif r > 150 and g > 120 and b < 100:
            color = "MUSTARD_YELLOW"
        elif r < 100 and g > 150 and b < 100:
            color = "GREEN"
        elif r > 150 and g < 100 and b < 100:
            color = "RED"
        elif r < 50 and g < 50 and b < 50:
            color = "DARK"
        else:
            color = f"RGB({r},{g},{b})"
            
        if color != current_color:
            if current_color is not None:
                blocks.append((current_color, color_start, x - 1))
            current_color = color
            color_start = x
            
    blocks.append((current_color, color_start, w - 1))
    
    print("\nColor blocks detected along the middle horizontal line:")
    for b_type, start, end in blocks:
        if "RGB" not in b_type or (end - start) > 5:  # skip thin transition borders
            print(f"  {b_type}: from X={start} to X={end} (width={end - start + 1})")
else:
    print("Destination file does not exist.")
