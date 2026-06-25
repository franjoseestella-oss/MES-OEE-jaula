import shutil
import os

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\panel10_progress_1782368727502.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\verification_screenshot_future_hiding.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
