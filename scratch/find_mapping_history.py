import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/git_history_plan_dashboard.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_diff = False
current_commit = ""
for line in lines:
    if line.startswith("commit "):
        current_commit = line.strip()
    elif line.startswith("@@ "):
        in_diff = True
    elif line.startswith("diff --git"):
        in_diff = False
    
    if in_diff:
        stripped = line.strip()
        if (stripped.startswith("+") or stripped.startswith("-")) and not (stripped.startswith("+++") or stripped.startswith("---")):
            # Check if this line is NOT SQL (doesn't contain typical SQL syntax and is typical JSON)
            if any(k in stripped for k in ["color", "value", "text", " Esperando", " Alarma", " Exceso", " Proceso", "Esperando máquina", "Exceso de tiempo"]):
                if not any(sql_k in stripped for sql_k in ["SELECT", "WHEN", "THEN", "AND", "EXISTS", "RawTimestamps", "AlarmIntervals", "COALESCE", "FROM"]):
                    print(f"{current_commit}: {line.strip()}")
