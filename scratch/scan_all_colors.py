from PIL import Image
import collections

img_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch\media__1782729162431.png"
img = Image.open(img_path)
w, h = img.size

color_counts = collections.Counter()
color_coords = collections.defaultdict(list)

for y in range(h):
    for x in range(w):
        r, g, b, a = img.getpixel((x, y))
        # simplify color a bit
        color_key = (r, g, b)
        color_counts[color_key] += 1
        color_coords[color_key].append((x, y))

# Print most common colors
print("Most common colors:")
for color, count in color_counts.most_common(10):
    print(f"  RGB{color}: {count} pixels")

# Look specifically for green/yellow/etc
print("\nScanning for active states:")
for color, count in color_counts.items():
    r, g, b = color
    # Skip dark colors
    if r < 50 and g < 50 and b < 50:
        continue
    # Classify
    if r > 180 and g > 180 and b < 100:
        name = "Bright Yellow"
    elif r > 150 and g > 120 and b < 100:
        name = "Mustard Yellow"
    elif r < 100 and g > 150 and b < 100:
        name = "Green"
    elif r > 150 and g < 100 and b < 100:
        name = "Red"
    else:
        name = "Other"
        
    if name != "Other" or count > 50:
        xs = [c[0] for c in color_coords[color]]
        ys = [c[1] for c in color_coords[color]]
        print(f"  {name} RGB{color}: {count} pixels, X range: [{min(xs)}, {max(xs)}], Y range: [{min(ys)}, {max(ys)}]")
