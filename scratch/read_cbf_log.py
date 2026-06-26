import os

target_path = r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e"
logs_dir = os.path.join(target_path, ".system_generated", "logs")
if os.path.exists(logs_dir):
    print("Listing logs_dir:", logs_dir)
    print(os.listdir(logs_dir))
    overview_file = os.path.join(logs_dir, "overview.txt")
    if os.path.exists(overview_file):
        print("overview.txt size:", os.path.getsize(overview_file))
else:
    # Check if there is an overview.txt somewhere in target_path
    print("logs_dir does not exist. Walking target_path...")
    for root, dirs, files in os.walk(target_path):
        for f in files:
            if "overview" in f or "log" in f:
                print(os.path.join(root, f))
