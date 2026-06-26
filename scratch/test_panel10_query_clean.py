import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
)

def run_query(plot_date, active_bastidor, active_start_dt):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        with open("scratch/panel10_query_full.sql", "r", encoding="utf-8") as f:
            query = f.read()
        
        # Replace the active sequence SELECT TOP 1 with mocks
        old_select_active = """SELECT TOP 1 
    @ActiveBastidor = NBASTIDOR,
    @ActiveStartDT = DATEADD(hour, -@UTCOffset, TRY_CONVERT(DATETIME, 
        SUBSTRING(FECHA_INICIO_CICLO, 13, 4) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 10, 2) + '-' + 
        SUBSTRING(FECHA_INICIO_CICLO, 7, 2) + 'T' + 
        SUBSTRING(FECHA_INICIO_CICLO, 1, 5) + ':00'
    ))
FROM dbo.REFERENCIA_EN_CICLO
WHERE LEN(FECHA_INICIO_CICLO) >= 16;"""

        new_select_active = f"""SET @ActiveBastidor = '{active_bastidor}';\nSET @ActiveStartDT = '{active_start_dt}';"""
        query = query.replace(old_select_active, new_select_active)
        
        # Replace $__timeFrom() with the plot_date
        query = query.replace("$__timeFrom()", f"'{plot_date}T00:00:00Z'")
        
        # Simplify FilteredTimestamps and boundaries
        # We find the FilteredTimestamps CTE and replace it
        target_where = """    WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND (s.actual_start < s.planned_start OR s.actual_start >= s.planned_end) THEN s.actual_start 
                      ELSE s.planned_start 
                  END
      AND bt.t <= CASE 
                      -- Rule: If a previous sequence is in progress, do not draw this sequence
                      WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL THEN
                          s.planned_start
                      
                      WHEN s.actual_start IS NOT NULL THEN
                          CASE 
                              WHEN s.actual_end IS NOT NULL THEN 
                                  CASE WHEN s.actual_end > s.planned_end THEN s.actual_end ELSE s.planned_end END
                              ELSE @CurrentProgressTime
                          END
                      ELSE
                          CASE 
                              WHEN s.planned_start >= @CurrentProgressTime THEN s.planned_start
                              ELSE
                                  CASE 
                                      WHEN s.planned_end > @CurrentProgressTime THEN @CurrentProgressTime
                                      ELSE s.planned_end
                                  END
                          END
                  END"""
                  
        replacement_where = """    WHERE bt.t >= CASE 
                      WHEN s.actual_start IS NOT NULL AND s.actual_start < s.planned_start THEN s.actual_start 
                      ELSE s.planned_start 
                  END
      AND bt.t <= CASE 
                      WHEN s.actual_end IS NOT NULL THEN s.actual_end
                      WHEN s.actual_start IS NOT NULL THEN @CurrentProgressTime
                      ELSE s.planned_end
                  END"""
                  
        query = query.replace(target_where, replacement_where)
        
        # Also replace any occurrences of `@ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL` in the SELECT clause
        old_select_active_block = """CASE 
                            -- Rule: If a previous sequence is in progress, do not draw this sequence
                            WHEN @ActiveSlotIdx IS NOT NULL AND s.slot_idx > @ActiveSlotIdx AND s.actual_start IS NULL THEN
                                s.planned_start
                            
                            WHEN s.actual_start IS NOT NULL THEN
                                CASE 
                                    WHEN s.actual_end IS NOT NULL THEN 
                                        CASE WHEN s.actual_end > s.planned_end THEN s.actual_end ELSE s.planned_end END
                                    ELSE @CurrentProgressTime
                                END
                            ELSE
                                CASE 
                                    WHEN s.planned_start >= @CurrentProgressTime THEN s.planned_start
                                    ELSE
                                        CASE 
                                            WHEN s.planned_end > @CurrentProgressTime THEN @CurrentProgressTime
                                            ELSE s.planned_end
                                        END
                                END
                        END"""
                        
        replacement_select_active_block = """CASE 
                            WHEN s.actual_end IS NOT NULL THEN s.actual_end
                            WHEN s.actual_start IS NOT NULL THEN @CurrentProgressTime
                            ELSE s.planned_end
                        END"""
                        
        query = query.replace(old_select_active_block, replacement_select_active_block)

        query = "SET NOCOUNT ON;\n" + query
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"\nResults for {plot_date} (Active: {active_bastidor} at {active_start_dt}):")
        print(f"Total rows returned: {len(rows)}")
        metrics = sorted(list(set(r[1].replace('\n', ' ') for r in rows)))
        print(f"Unique metrics in result ({len(metrics)}):")
        for m in metrics:
            print(f" - {m}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # Test 1: Plotting June 29, 2026 (future date) with active sequence starting on June 26
    # Active sequence is SFB09E704696 (sequence 0292), which started on June 26 at 05:54:00 UTC (07:54:00 local)
    run_query(plot_date="2026-06-29", active_bastidor="SFB09E704696", active_start_dt="2026-06-26T05:54:00Z")
