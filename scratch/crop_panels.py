from PIL import Image

img_path = r"C:\Users\franj\.gemini\antigravity\brain\46c0d72d-af9f-4c64-a95c-26ada40c615f\panel_14_labels_test.png"
out_path = r"C:\Users\franj\.gemini\antigravity\brain\46c0d72d-af9f-4c64-a95c-26ada40c615f\panel_14_cropped.png"

img = Image.open(img_path)
width, height = img.size
print(f"Image dimensions: {width}x{height}")

# Crop the middle/lower section where panels 14 and 15 should be
# Panel 14 is left half, Panel 15 is right half.
# Let's crop from y = 0.3 * height to 0.9 * height
top = int(0.25 * height)
bottom = int(0.95 * height)
cropped = img.crop((0, top, width, bottom))
cropped.save(out_path)
print(f"Cropped image saved to: {out_path}")
