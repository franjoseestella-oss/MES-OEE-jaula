with open("scratch/panel10_current.sql", "r", encoding="utf-16-le") as f:
    content = f.read()
with open("scratch/panel10_current_utf8.sql", "w", encoding="utf-8") as f:
    f.write(content)
