import shutil

src = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\dashboard_loaded_1782377427134.png"
dst = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e\plan_evolution_chart_verification.png"

shutil.copyfile(src, dst)
print("Copied successfully to:", dst)
