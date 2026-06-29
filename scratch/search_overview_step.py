import re

path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find "422" and print some surrounding context (e.g. 1000 characters before and after)
pos = content.find('"Instruction":"\\"Insert a WHEN clause for yellow status')
if pos != -1:
    print("Found instruction at position:", pos)
    print(content[pos-500:pos+1500])
else:
    # Try finding "422"
    matches = [m.start() for m in re.finditer(r'"step_index":\s*422\b', content)]
    print(f"Matches for step 422: {matches}")
    for m in matches:
        print(content[m-200:m+2000])
