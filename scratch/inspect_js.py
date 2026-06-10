with open("scratch/5017.aaaa340b86e350c74a1e.js", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer("threshold1", content)]
print("Total matches:", len(matches))
for i, idx in enumerate(matches):
    print(f"\nMatch {i+1} at {idx}:")
    print(content[max(0, idx - 150):min(len(content), idx + 350)])
