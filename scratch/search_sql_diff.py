import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/diff_92178e9.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_sql = False
sql_lines = []
for line in lines:
    if '"rawSql"' in line or 'SELECT' in line or 'WITH' in line or 'DECLARE' in line:
        in_sql = True
    if in_sql:
        sql_lines.append(line)
        if len(sql_lines) > 200:
            # Let's write them out or print them
            break

print("Found lines:")
for l in sql_lines[:150]:
    if l.startswith("+") or l.startswith("-"):
        print(l.strip())
