import pyodbc
import re

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

def main():
    with open("scratch/panel_10_A.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    # 1. Add TheoreticalActiveSlotIdx declaration and calculation
    old_active_slot_calc = """-- Find active slot index in progress
DECLARE @ActiveSlotIdx INT;
SELECT @ActiveSlotIdx = MIN(slot_idx)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;"""

    new_active_slot_calc = """-- Find active slot index in progress
DECLARE @ActiveSlotIdx INT;
SELECT @ActiveSlotIdx = MIN(slot_idx)
FROM #SeqsToSchedule
WHERE actual_start IS NOT NULL AND actual_end IS NULL;

-- Find theoretical active slot index
DECLARE @TheoreticalActiveSlotIdx INT;
SELECT TOP 1 @TheoreticalActiveSlotIdx = slot_idx
FROM #SeqsToSchedule
WHERE planned_start <= @CurrentProgressTime AND planned_end >= @CurrentProgressTime;

IF @TheoreticalActiveSlotIdx IS NULL
BEGIN
    SELECT @TheoreticalActiveSlotIdx = COALESCE(
        (SELECT MAX(slot_idx) FROM #SeqsToSchedule WHERE planned_start <= @CurrentProgressTime),
        1
    );
END;"""

    if old_active_slot_calc not in sql:
        print("Error: Could not find @ActiveSlotIdx calculation block in SQL file.")
        return

    sql = sql.replace(old_active_slot_calc, new_active_slot_calc)

    # 2. Modify rule condition in FilteredTimestamps and Active states SELECT
    old_rule_cond = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL THEN"
    new_rule_cond = "WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL AND @ActiveSlotIdx >= @TheoreticalActiveSlotIdx THEN"

    occurrences = sql.count(old_rule_cond)
    print(f"Found {occurrences} occurrences of the rule condition.")
    
    sql = sql.replace(old_rule_cond, new_rule_cond)

    with open("scratch/panel_10_out_of_order_fix.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print("Saved modified query to scratch/panel_10_out_of_order_fix.sql")

    # Mocks for testing:
    # We will replace $__timeFrom() with a date we have data for, e.g. June 24 or 26.
    # Let's test with June 26.
    test_sql = sql.replace("$__timeFrom()", "'2026-06-26T00:00:00Z'")

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Running query on SQL Server...")
        cursor.execute("SET NOCOUNT ON;\n" + test_sql)
        rows = cursor.fetchall()
        print(f"Success! Query executed successfully. Returned {len(rows)} rows.")
        if len(rows) > 0:
            print("First 5 rows:")
            for r in rows[:5]:
                print(r)
        cursor.close()
        conn.close()
    except Exception as e:
        print("SQL Server execution error:", e)

if __name__ == "__main__":
    main()
