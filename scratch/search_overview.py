import re

path = r"C:\Users\franj\.gemini\antigravity\brain\a010f07c-a801-484a-b8b6-193103479774\.system_generated\logs\overview.txt"
# Try reading with different encodings
for enc in ['utf-8', 'utf-16', 'utf-16-le', 'latin-1']:
    try:
        with open(path, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Successfully read with {enc}, length = {len(content)}")
        # Look for "alarma", "restablece", "amarillo", "rojo"
        for word in ["alarma", "restablece", "amarillo", "rojo", "yellow"]:
            matches = [m.start() for m in re.finditer(word, content, re.IGNORECASE)]
            print(f"  Word '{word}': {len(matches)} matches")
            if matches:
                # Print a few snippets
                for idx in matches[:5]:
                    start = max(0, idx - 50)
                    end = min(len(content), idx + 50)
                    print(f"    Snippet: {repr(content[start:end])}")
        break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
