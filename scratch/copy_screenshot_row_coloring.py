import shutil

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\row_coloring_verification_1782387478819.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\plan_row_coloring_verification.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
