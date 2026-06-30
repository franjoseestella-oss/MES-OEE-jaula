import os
from PIL import Image

image1 = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\media__1782821527853.png"
image2 = r"C:\Users\franj\.gemini\antigravity\brain\89948a07-0b4c-4cea-9b1e-2a96be661f8a\.tempmediaStorage\media_89948a07-0b4c-4cea-9b1e-2a96be661f8a_1782821743896.png"

for img_path in [image1, image2]:
    if not os.path.exists(img_path):
        print(f"{img_path} does not exist.")
        continue
    print(f"\n--- OCR for {os.path.basename(img_path)} ---")
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(img_path))
        print("Pytesseract text:")
        print(text)
    except Exception as e:
        print("Pytesseract failed:", e)

    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'])
        result = reader.readtext(img_path, detail=0)
        print("EasyOCR text:")
        print(result)
    except Exception as e:
        print("EasyOCR failed:", e)
