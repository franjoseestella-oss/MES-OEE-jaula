import os

prev_session_dir = r"C:\Users\franj\.gemini\antigravity\brain\94f80dcf-f9fc-46d5-8664-bf671481cae2"

json_files = []
for root, dirs, files in os.walk(prev_session_dir):
    for file in files:
        if file.endswith(".json") or file.endswith(".txt") or file.endswith(".py"):
            full_path = os.path.join(root, file)
            # check size
            size = os.path.getsize(full_path)
            if size > 100:
                json_files.append((full_path, size))

print(f"Found {len(json_files)} files in previous session directory:")
for path, size in sorted(json_files, key=lambda x: x[1], reverse=True)[:30]:
    print(f" - {path} ({size} bytes)")
