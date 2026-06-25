import shutil

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\registro_today_status_1782375696400.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\registro_today_status.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
