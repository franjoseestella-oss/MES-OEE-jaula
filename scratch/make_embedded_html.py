import base64
import os

def to_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

b64_1 = to_base64("artifacts/media1.png")
b64_2 = to_base64("artifacts/media2.png")

html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Inspect Screenshots</title>
    <style>
        body {{
            background-color: #1e222b;
            color: #ffffff;
            font-family: Arial, sans-serif;
            padding: 20px;
        }}
        .image-container {{
            margin-bottom: 40px;
            border: 2px solid #3e4451;
            padding: 10px;
            background-color: #282c34;
            display: inline-block;
        }}
        h2 {{
            margin-top: 0;
            color: #61afef;
        }}
        img {{
            display: block;
            max-width: 100%;
            border: 1px solid #abb2bf;
        }}
    </style>
</head>
<body>
    <h1>Compare Screenshots</h1>
    
    <div class="image-container">
        <h2>media1.png (Original/Reference)</h2>
        <img src="data:image/png;base64,{b64_1}" alt="media1">
    </div>
    
    <div class="image-container">
        <h2>media2.png (Current/With Highlight)</h2>
        <img src="data:image/png;base64,{b64_2}" alt="media2">
    </div>
</body>
</html>
"""

with open("artifacts/view.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated artifacts/view.html successfully.")
