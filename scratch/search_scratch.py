import os
import re

scratch_dir = "scratch"
pattern = re.compile(r"(salte|saltar|skip|color|exceso|active|completa)", re.IGNORECASE)

output_lines = []

for root, dirs, files in os.walk(scratch_dir):
    for file in files:
        if file.endswith(('.txt', '.py', '.sql', '.json', '.md', '.diff')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                try:
                    with open(path, 'r', encoding='utf-16') as f:
                        content = f.read()
                except Exception:
                    continue
            
            matches = list(pattern.finditer(content))
            if matches:
                output_lines.append(f"File {path} has {len(matches)} matches.")
                for m in matches[:5]:
                    start = max(0, m.start() - 60)
                    end = min(len(content), m.end() + 60)
                    snippet = content[start:end].replace('\n', ' ')
                    output_lines.append(f"  Snippet: ... {snippet} ...")

with open("scratch/search_results_output.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(output_lines))
print("Done writing to scratch/search_results_output.txt")
