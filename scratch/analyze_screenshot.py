from PIL import Image
import numpy as np

# Load the copied screenshot
img = Image.open('C:/Users/franj/.gemini/antigravity/brain/70912b51-1041-4be2-9d46-655465e25ab2/artifacts/gauge_screenshot.png')
w, h = img.size
print(f"Screenshot resolution: {w}x{h}")

# Convert to numpy array
arr = np.array(img)

# Define HSL / RGB color ranges for:
# - Grafana Green: #2FD06A -> RGB(47, 208, 106)
# - Grafana Red: #E32636 -> RGB(227, 38, 54)
# Let's count pixels matching these colors with some tolerance

green_pixels = 0
red_pixels = 0

for y in range(h):
    for x in range(w):
        r, g, b = arr[y, x][:3]
        
        # Check green (#2FD06A / #56A64B / #73BF69 etc.)
        # Green has high g and relatively low r/b
        if g > 150 and r < 120 and b < 120:
            green_pixels += 1
            
        # Check red (#E32636 / #F2495C / #FF7383 etc.)
        # Red has high r and relatively low g/b
        if r > 180 and g < 100 and b < 100:
            red_pixels += 1

print(f"Green pixels: {green_pixels}")
print(f"Red pixels: {red_pixels}")
