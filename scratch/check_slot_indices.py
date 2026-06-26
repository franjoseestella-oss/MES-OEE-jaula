import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

def main():
    # Read query SQL
    with open("scratch/panel_10_out_of_order_fix.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    # Replace $__timeFrom() with '2026-06-25T00:00:00Z'
    sql = sql.replace("$__timeFrom()", "'2026-06-25T00:00:00Z'")

    # Let's extract the part that builds temp tables and does the select variables
    pos = sql.find("WITH AlarmIntervals AS")
    if pos == -1:
        print("Could not find WITH AlarmIntervals AS")
        return

    test_part = sql[:pos] + """
SELECT 
    @ActiveSlotIdx AS ActiveSlotIdx,
    @TheoreticalActiveSlotIdx AS TheoreticalActiveSlotIdx,
    @CurrentProgressTime AS CurrentProgressTime,
    @ShiftStartDT AS ShiftStartDT,
    @ShiftEndDT AS ShiftEndDT;

SELECT 
    slot_idx, secuencia, bastidor, status, completed,
    planned_start, planned_end, actual_start, actual_end
FROM #SeqsToSchedule
ORDER BY slot_idx;
"""

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Enable multiple results
    cursor.execute("SET NOCOUNT ON;\n" + test_part)
    
    # First result: variables
    vars_row = cursor.fetchone()
    print("Variables:")
    print(f"  ActiveSlotIdx: {vars_row[0]}")
    print(f"  TheoreticalActiveSlotIdx: {vars_row[1]}")
    print(f"  CurrentProgressTime: {vars_row[2]}")
    print(f"  ShiftStartDT: {vars_row[3]}")
    print(f"  ShiftEndDT: {vars_row[4]}")
    
    # Second result: SeqsToSchedule
    cursor.nextset()
    print("\n#SeqsToSchedule:")
    for r in cursor.fetchall():
        print(f"  Slot {r[0]}: Seq={r[1]}, Bastidor={r[2]}, Status={r[3]}, Completed={r[4]}")
        print(f"    Planned: {r[5]} to {r[6]}")
        print(f"    Actual:  {r[7]} to {r[8]}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
