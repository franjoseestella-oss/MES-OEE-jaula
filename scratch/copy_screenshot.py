import shutil
import os

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\.tempmediaStorage\media_a961276b-cf64-4f02-b78b-201b21659b4e_1782368060618.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\verification_screenshot_transitions.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
