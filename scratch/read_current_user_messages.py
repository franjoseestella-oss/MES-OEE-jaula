import os
import sys

# Reconfigure stdout to use utf-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

target_dirs = [
    r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774",
    r"C:\Users\franj\.gemini\antigravity\brain\dd598c2e-2ed4-42b6-930c-47a6d577420e",
    r"C:\Users\franj\.gemini\antigravity\brain\a961276b-cf64-4f02-b78b-201b21659b4e"
]

keywords = ["amarillo", "azul", "gris", "color", "timeline", "registro", "manten", "quites", "secuencia"]

out_lines = []

for d in target_dirs:
    overview_path = os.path.join(d, ".system_generated", "logs", "overview.txt")
    if os.path.exists(overview_path):
        out_lines.append(f"\n=== LOGS FROM {os.path.basename(d)} ===\n")
        with open(overview_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            # Check if any keyword matches case insensitively
            if any(k in line.lower() for k in keywords):
                # Print line with surrounding context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                out_lines.append(f"--- Line {i} ---\n")
                for j in range(start, end):
                    out_lines.append(f"{j}: {lines[j].strip()}\n")

output_file = r"scratch/search_results.txt"
with open(output_file, "w", encoding="utf-8") as out_f:
    out_f.writelines(out_lines)

print(f"Done! Written to {output_file}")
