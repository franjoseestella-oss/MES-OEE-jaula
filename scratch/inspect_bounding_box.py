import os
from PIL import Image

def inspect_box(path, name):
    print(f"=== Bounding box in {name} ===")
    if not os.path.exists(path):
        print("File does not exist.")
        return
    img = Image.open(path)
    # Let's count colors inside X=[548, 617], Y=[0, 50]
    box = img.crop((548, 0, 617, 50))
    colors = box.getcolors(box.width * box.height)
    if colors:
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
        print("Top colors inside the box:")
        for count, rgba in sorted_colors[:10]:
            print(f"  {rgba}: {count} pixels ({count/(box.width*box.height)*100:.1f}%)")

inspect_box("artifacts/media1.png", "media1.png")
inspect_box("artifacts/media2.png", "media2.png")
