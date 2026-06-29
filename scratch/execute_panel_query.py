import json


# Connect directly to database or use grafana-mcp
# Let's read query_06.sql and replace Grafana macros with values
with open("scratch/query_06.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# Replace $__timeFrom() with a DATETIME literal
sql_mod = sql.replace("$__timeFrom()", "'2026-06-29T07:00:00Z'")

print("Query modified. Let's execute via Grafana MCP.")

# We will execute the query using mcp_grafana-mcp_query_sql_datasource
# Let's save the modified SQL to scratch/query_to_run.sql
with open("scratch/query_to_run.sql", "w", encoding="utf-8") as f:
    f.write(sql_mod)
