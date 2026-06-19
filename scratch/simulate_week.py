import pyodbc
from datetime import datetime, timedelta

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PMRMSPT\\SQLEXPRESS,1435;"
    "DATABASE=DAFEED;"
    "UID=usuario_readonly;"
    "PWD=Logisnext2026!;"
    "TrustServerCertificate=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get all sequences in JAULA_ERP for the week 2026-06-15 to 2026-06-19
cursor.execute("""
SELECT id, secuencia, bastidor, modelo, fecha_montaje
FROM JAULA_ERP
WHERE fecha_montaje BETWEEN '20260615' AND '20260619'
ORDER BY id
""")
erp_sequences = [
    {
        "id": r[0],
        "secuencia": r[1],
        "bastidor": r[2],
        "modelo": r[3],
        "original_date": datetime.strptime(r[4], "%Y%m%d").date(),
        "scheduled_date": None,
        "planned_start": None,
        "planned_end": None,
        "completed": False,
        "completion_time": None,
        "status": "Pendiente"
    }
    for r in cursor.fetchall()
]

# Get all logs for this week
cursor.execute("""
SELECT id, NSECUENCIA, NBASTIDOR, OK_NOK, FECHA_HORA_INICIO_SEC, FECHA_HORA_FIN_SEC, FECHA_MONTAJE
FROM LOG_TABLA
WHERE FECHA_MONTAJE BETWEEN '2026-06-15' AND '2026-06-19'
ORDER BY id
""")
logs = cursor.fetchall()

# Map logs to sequences
# A sequence is completed if there is an OK/NOK log for the bastidor and date
for seq in erp_sequences:
    # Find matching log
    for log in logs:
        if log[2] == seq["bastidor"] and log[6].date() == seq["original_date"]:
            seq["completed"] = True
            seq["status"] = log[3]
            seq["completion_time"] = log[5]  # FECHA_HORA_FIN_SEC

# Get planned shift capacities
days_of_week = [
    datetime(2026, 6, 15).date() + timedelta(days=i)
    for i in range(5)
]

capacities = {}
for d in days_of_week:
    cursor.execute("SELECT Cant_A_Fabricar FROM CALENDARIO_LABORAL WHERE Fecha = ?", (d,))
    row = cursor.fetchone()
    capacities[d] = int(row[0]) if row else 18

# Load HHSS schedules
schedules = {}
for cap in [18, 19]:
    cursor.execute(f"SELECT horario FROM dbo.HHSS_{cap} ORDER BY id")
    schedules[cap] = [r[0] for r in cursor.fetchall()]

# Simulation of scheduling
# We process day by day from Monday to Friday
pending_queue = []
erp_by_date = {d: [] for d in days_of_week}
for seq in erp_sequences:
    erp_by_date[seq["original_date"]].append(seq)

print("--- RUNNING SIMULATION ---")
for d in days_of_week:
    capacity = capacities[d]
    day_schedule = schedules.get(capacity, schedules[18])
    
    # The queue of sequences to schedule today consists of:
    # 1. Pending sequences carried over
    # 2. Sequences originally planned for today
    today_queue = pending_queue + erp_by_date[d]
    pending_queue = []
    
    scheduled_today = []
    # Fill the slots
    for i in range(min(len(today_queue), len(day_schedule))):
        seq = today_queue[i]
        seq["scheduled_date"] = d
        
        # Calculate planned times
        shift_start = datetime.combine(d, datetime.min.time()) + timedelta(hours=7)
        if i == 0:
            seq["planned_start"] = shift_start
        else:
            prev_time = day_schedule[i-1]
            seq["planned_start"] = datetime.combine(d, datetime.min.time()) + timedelta(hours=prev_time.hour, minutes=prev_time.minute, seconds=prev_time.second)
            
        curr_time = day_schedule[i]
        seq["planned_end"] = datetime.combine(d, datetime.min.time()) + timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=curr_time.second)
        
        scheduled_today.append(seq)
        
    print(f"\nDate: {d} (Capacity: {capacity})")
    print(f"Queue size at start: {len(today_queue)}")
    print(f"Scheduled today: {len(scheduled_today)}")
    for i, seq in enumerate(scheduled_today):
        print(f"  Slot {i+1:02d}: Seq={seq['secuencia']} Bastidor={seq['bastidor']} Status={seq['status']} ScheduledStart={seq['planned_start'].time()} OrigDate={seq['original_date']}")
        
    # Any sequence in today_queue that was not scheduled today OR was scheduled but not completed is pending!
    for idx, seq in enumerate(today_queue):
        if seq not in scheduled_today:
            pending_queue.append(seq)
        elif not seq["completed"]:
            pending_queue.append(seq)

print(f"\nRemaining pending queue for next week: {len(pending_queue)}")
