import os

base_dir = r"C:\Users\franj\.gemini\antigravity"
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".md"):
            print(os.path.join(root, f))
