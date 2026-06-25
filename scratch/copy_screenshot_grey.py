import shutil

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\grey_early_start_verification_1782389202757.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\timeline_verification_early_start_grey.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
