import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app_data = r"C:\Users\franj\.gemini\antigravity"
prev_conv_id = "94f80dcf-f9fc-46d5-8664-bf671481cae2"
target_dir = os.path.join(app_data, "brain", prev_conv_id)

print(f"Scanning recursively in {target_dir}...")
if os.path.exists(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, target_dir)
            print(f" - {rel_path} ({os.path.getsize(full_path) / 1024.0:.2f} KB)")
else:
    print("Target directory not found.")
