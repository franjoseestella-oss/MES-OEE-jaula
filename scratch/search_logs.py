import os

brain_dir = r"C:\Users\franj\.gemini\antigravity\brain"

keywords = ["completada", "proceso", "coja", "last completed", "active", "en curso"]

for root, dirs, files in os.walk(brain_dir):
    # Only search inside .system_generated/logs
    if ".system_generated" in root and "logs" in root:
        for f in files:
            if f == "overview.txt" or f.endswith(".md"):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        content = file.read()
                    
                    if "completada" in content or "proceso" in content or "active" in content:
                        lines = content.splitlines()
                        printed_header = False
                        for idx, line in enumerate(lines):
                            if any(kw in line.lower() for kw in keywords) and ("user" in line.lower() or "model" in line.lower() or "system" in line.lower()):
                                if not printed_header:
                                    print(f"\nMatch found in: {path}")
                                    printed_header = True
                                print(f"  Line {idx+1}: {line[:150]}")
                except Exception as e:
                    pass
