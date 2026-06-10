import re

with open(r'c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION\frontend\src\components\Sequencer.jsx', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File length: {len(content)} characters")

# Find references to steps or stages
steps = re.findall(r'(?i)step|etapa|paso', content)
print(f"Occurrences of step/etapa/paso: {len(steps)}")

# Print lines containing '3' or 'Step 3' or 'Paso 3'
lines = content.split('\n')
for idx, line in enumerate(lines):
    if 'Paso 3' in line or 'Paso 2' in line or 'Paso 4' in line or 'Step 3' in line:
        print(f"Line {idx+1}: {line.strip()[:100]}")
