import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_dirs = [
    r"C:\Users\franj\.gemini\antigravity\brain\5fb9b6d4-078a-4d9e-b78a-22db34c6505a",
    r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch"
]

keywords = ["vertical", "timeline", "secuencia", "estado"]

for search_dir in search_dirs:
    if not os.path.exists(search_dir):
        continue
    print(f"Searching in: {search_dir}")
    for root, dirs, files in os.walk(search_dir):
        # Skip media storage and build files
        if ".git" in root or ".tempmediaStorage" in root:
            continue
        for file in files:
            if not file.endswith((".py", ".txt", ".json", ".md")):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content.lower():
                        # Find occurrences
                        lines = content.splitlines()
                        for idx, l in enumerate(lines):
                            if kw in l.lower() and len(l) < 200:
                                print(f"[{file}:{idx+1}] ({kw}) {l.strip()}")
            except Exception as e:
                pass
