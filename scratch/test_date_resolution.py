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

def test_date(test_date_str):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    query = """
    DECLARE @ActiveDate VARCHAR(8);
    SET @ActiveDate = CONVERT(varchar(8), CAST(? AS DATE), 112);

    IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    BEGIN
        SET @ActiveDate = COALESCE(
            (SELECT TOP 1 FECHA_MONTAJE FROM LOG_TABLA WHERE CAST(fecha_creacion AS DATE) = CAST(? AS DATE) ORDER BY id DESC),
            (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
            (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
            (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
        );
    END;

    SELECT @ActiveDate AS ResolvedDate, (SELECT COUNT(*) FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate) AS CountSeqs;
    """
    
    cursor.execute(query, (test_date_str, test_date_str))
    r = cursor.fetchone()
    print(f"For Input Date '{test_date_str}': Resolved Date = '{r[0]}', Seqs Count = {r[1]}")
    conn.close()

if __name__ == "__main__":
    test_date("2026-06-12")
