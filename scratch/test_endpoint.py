import pyodbc
import requests

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
    "ConnLifetime=30;"
)

def check_nok():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, NSECUENCIA, OK_NOK FROM LOG_TABLA WHERE id = 8037")
    row = cursor.fetchone()
    print(f"Before endpoint call: id={row[0]}, NSECUENCIA={row[1]}, OK_NOK={row[2]}")
    conn.close()

def call_endpoint():
    url = "http://localhost:8000/api/v1/sequences/8037/force-ok"
    r = requests.get(url, allow_redirects=False)
    print(f"Endpoint response status: {r.status_code}")
    print(f"Headers: {r.headers}")

def check_ok():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, NSECUENCIA, OK_NOK FROM LOG_TABLA WHERE id = 8037")
    row = cursor.fetchone()
    print(f"After endpoint call: id={row[0]}, NSECUENCIA={row[1]}, OK_NOK={row[2]}")
    conn.close()

if __name__ == "__main__":
    check_nok()
    call_endpoint()
    check_ok()
