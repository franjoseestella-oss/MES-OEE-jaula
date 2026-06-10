import re

with open(r'c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION\frontend\src\components\Sequencer.jsx', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.split('\n')
out = []
# Search for lines around Step 3 logic
for idx, line in enumerate(lines):
    # Search for Paso 3 or step3 or similar
    if any(q in line for q in ['Paso 3', 'Paso 2', 'Paso 4', 'Step 3', 'step 3', 'ETAPA 3', 'Etapa 3']):
        out.append(f"Line {idx+1}: {line.strip()}")
    # Search for occurrences of MIN or MAX in JSX
    if ('min' in line.lower() or 'max' in line.lower()) and ('<' in line or 'className' in line or '{' in line):
        out.append(f"Line {idx+1}: {line.strip()}")

with open('scratch/sequencer_search_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f"Search done. Wrote {len(out)} results to scratch/sequencer_search_results.txt")
