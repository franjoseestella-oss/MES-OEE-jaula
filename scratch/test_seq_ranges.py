import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

def inspect():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    dates_to_test = ['2026-06-24', '2026-06-25', '2026-06-26', '2026-06-27', '2026-06-29', '2026-06-30']
    
    for d in dates_to_test:
        sql = f"""
        DECLARE @SelectedDate DATE = '{d}';
        DECLARE @BaseDate DATE = '2026-06-24';
        DECLARE @BaseSeq INT = 227;
        DECLARE @StartSeq INT, @EndSeq INT;

        IF @SelectedDate < @BaseDate
        BEGIN
            SELECT @StartSeq = @BaseSeq - COALESCE(SUM(Cant_A_Fabricar), 0)
            FROM dbo.CALENDARIO_LABORAL
            WHERE Fecha >= @SelectedDate AND Fecha < @BaseDate AND Laborable = 1;
        END
        ELSE
        BEGIN
            SELECT @StartSeq = @BaseSeq + COALESCE(SUM(Cant_A_Fabricar), 0)
            FROM dbo.CALENDARIO_LABORAL
            WHERE Fecha >= @BaseDate AND Fecha < @SelectedDate AND Laborable = 1;
        END;

        DECLARE @DayCap INT;
        SELECT @DayCap = COALESCE(Cant_A_Fabricar, 18)
        FROM dbo.CALENDARIO_LABORAL
        WHERE Fecha = @SelectedDate;

        SET @EndSeq = @StartSeq + @DayCap - 1;

        SELECT @StartSeq AS StartSeq, @EndSeq AS EndSeq, @DayCap AS DayCap;
        """
        cursor.execute(sql)
        r = cursor.fetchone()
        print(f"Date: {d} | StartSeq: {r[0]} | EndSeq: {r[1]} | DayCap: {r[2]}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
