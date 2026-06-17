import os

path = r"C:\Users\franj\.gemini\antigravity\browser_recordings\e1630d34-9f7f-44dc-8a18-8dfc6494f30c"
if os.path.exists(path):
    print("Files in", path)
    for f in os.listdir(path):
        print(f)
else:
    print("Folder does not exist:", path)
