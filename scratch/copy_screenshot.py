import shutil

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\timeline_verification_1782387896447.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\timeline_verification_green.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
