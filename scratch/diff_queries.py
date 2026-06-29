import difflib

with open("scratch/query_7f.sql", "r", encoding="utf-8") as f:
    lines_7f = f.readlines()

with open("scratch/query_06.sql", "r", encoding="utf-8") as f:
    lines_06 = f.readlines()

diff = difflib.unified_diff(lines_7f, lines_06, fromfile="query_7f.sql", tofile="query_06.sql")
for line in diff:
    print(line, end="")
