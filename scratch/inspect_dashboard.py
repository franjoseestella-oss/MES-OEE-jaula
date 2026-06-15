import json

file_path = r"C:/Users/franj/.gemini/antigravity/brain/2838449e-b6e8-4ec7-bb93-57e5af4c698b/.system_generated/steps/716/output.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# The get_dashboard endpoint might return a wrapper {"dashboard": {...}}
dashboard = data.get("dashboard", data)

target_titles = [
    "Elevacion Sin Carga",
    "Descenso Sin Carga",
    "Elevacion Con Carga",
    "Descenso Con Carga"
]

for panel in dashboard.get("panels", []):
    title = panel.get("title")
    if title in target_titles:
        print(f"=== Panel: {title} ===")
        print("Transformations:")
        print(json.dumps(panel.get("transformations"), indent=2))
        print("FieldConfigDefaults:")
        print(json.dumps(panel.get("fieldConfig", {}).get("defaults"), indent=2))
        print("\n")
