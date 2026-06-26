import os

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"
if os.path.exists(brain_dir):
    print("Listing directories in", brain_dir)
    for entry in os.listdir(brain_dir):
        full_path = os.path.join(brain_dir, entry)
        if os.path.isdir(full_path):
            print(f"Directory: {entry}")
else:
    print(f"{brain_dir} does not exist")
