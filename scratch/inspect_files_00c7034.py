import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/raw_show_00c7034.txt", "r", encoding="utf-16") as f:
    content = f.read()

import re
matches = re.findall(r"^diff --git a/(.*) b/(.*)$", content, flags=re.MULTILINE)
for match in matches:
    print(match[0])
