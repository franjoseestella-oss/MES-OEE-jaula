"""
Seed realistic OEE demo data into SQL Server via Grafana datasource proxy.
Uses the Grafana API to execute INSERT statements since pyodbc driver 18 is not installed locally.

Shift: 7:00 – 15:00 with lunch break 10:00 – 10:30
Reference image targets:
  OEE ~87.5%, Availability ~92.1%, Performance ~95.3%, Quality ~99.8%
  Production ~15,240 total, ~15,209 good, ~31 bad
  MTBF ~4h30m, MTTR ~15min
"""

import json
import urllib.request
import urllib.error
import base64
import datetime
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ── Grafana connection ─────────────────────────────────────────────────────────
GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"
DS_UID = "mes_sqlserver"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}


def grafana_sql(query):
    """Execute a SQL statement via Grafana datasource proxy."""
    payload = json.dumps({
        "queries": [{
            "refId": "A",
            "datasource": {"uid": DS_UID},
            "rawSql": query,
            "format": "table"
        }],
        "from": "now-1h",
        "to": "now"
    }).encode()
    req = urllib.request.Request(f"{GRAFANA_URL}/api/ds/query", data=payload, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [ERROR] {e.code}: {body[:200]}")
        return None


# ── Config ─────────────────────────────────────────────────────────────────────
MACHINE_ID = "MAQ-01"

# Today's shift: 7:00 to 15:00 with break 10:00-10:30
TODAY = datetime.date.today()
SHIFT_START = datetime.datetime(TODAY.year, TODAY.month, TODAY.day, 7, 0, 0)
SHIFT_END   = datetime.datetime(TODAY.year, TODAY.month, TODAY.day, 15, 0, 0)
BREAK_START = datetime.datetime(TODAY.year, TODAY.month, TODAY.day, 10, 0, 0)
BREAK_END   = datetime.datetime(TODAY.year, TODAY.month, TODAY.day, 10, 30, 0)

FMT = "%Y-%m-%dT%H:%M:%S"


def ensure_tables():
    """Create helper tables for stop/reject reasons if they don't exist."""
    grafana_sql("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'mes_stop_reasons')
        CREATE TABLE mes_stop_reasons (
            id INT IDENTITY(1,1) PRIMARY KEY,
            machine_id VARCHAR(50) NOT NULL,
            reason NVARCHAR(200) NOT NULL,
            duration_s INT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            created_at DATETIME DEFAULT GETDATE()
        )
    """)
    grafana_sql("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'mes_reject_reasons')
        CREATE TABLE mes_reject_reasons (
            id INT IDENTITY(1,1) PRIMARY KEY,
            machine_id VARCHAR(50) NOT NULL,
            reason NVARCHAR(200) NOT NULL,
            quantity INT NOT NULL,
            timestamp DATETIME NOT NULL,
            created_at DATETIME DEFAULT GETDATE()
        )
    """)
    print("  [OK] Helper tables ensured")


def clear_demo_data():
    """Remove today's demo data."""
    cutoff = SHIFT_START.strftime(FMT)
    grafana_sql(f"DELETE FROM mes_machine_events WHERE machine_id = '{MACHINE_ID}' AND timestamp >= '{cutoff}'")
    grafana_sql(f"DELETE FROM mes_oee_snapshots WHERE machine_id = '{MACHINE_ID}' AND ts >= '{cutoff}'")
    grafana_sql(f"DELETE FROM mes_stop_reasons WHERE machine_id = '{MACHINE_ID}' AND start_time >= '{cutoff}'")
    grafana_sql(f"DELETE FROM mes_reject_reasons WHERE machine_id = '{MACHINE_ID}' AND timestamp >= '{cutoff}'")
    grafana_sql(f"DELETE FROM mes_machine_events WHERE machine_id = '{MACHINE_ID}' AND state = 'Disconnected'")
    print("  [OK] Cleared old demo data")


def seed_machine_events():
    """
    Insert machine state events for the 7:00-15:00 shift.
    States: Running (1), Stopped (0), Setup (2), Micro-stop (3), Break (4)
    Returns: list of events, total_good, total_bad
    """
    events = []
    t = SHIFT_START
    now = datetime.datetime.now()
    end = min(SHIFT_END, now)

    # Fetch today's sequences to map them
    active_date_erp = TODAY.strftime("%Y%m%d")
    res = grafana_sql(f"SELECT secuencia FROM dbo.JAULA_ERP WHERE fecha_montaje = '{active_date_erp}' ORDER BY id")
    seq_list = []
    try:
        if res and "results" in res:
            frames = res["results"]["A"]["frames"]
            if frames and len(frames) > 0:
                data = frames[0]["data"]
                if data and "values" in data and len(data["values"]) > 0:
                    seq_list = data["values"][0]
    except Exception as e:
        print(f"  [WARNING] Could not fetch sequences for today: {e}")

    while t < end:
        # Lunch break
        if BREAK_START <= t < BREAK_END:
            events.append({
                "state": "Break", "state_code": 4,
                "start": t, "end": min(BREAK_END, end),
                "pieces": 0, "good": 0, "bad": 0, "reason": "Almuerzo"
            })
            t = min(BREAK_END, end)
            continue

        # Don't go past break start or end
        next_boundary = end
        if t < BREAK_START:
            next_boundary = min(BREAK_START, end)

        r = random.random()
        if r < 0.65:
            # Running — 8 to 30 min blocks
            dur = random.randint(8, 30)
            state, code = "Running", 1
            # ~2 pieces per minute (realistic for forklift testing cycle)
            pieces = int(dur * random.uniform(1.8, 2.2))
            bad = 1 if random.random() < 0.003 else 0  # ~0.3% defect rate
            good = pieces - bad
        elif r < 0.80:
            # Stopped (unplanned)
            dur = random.randint(8, 25)
            state, code = "Stopped", 0
            pieces, good, bad = 0, 0, 0
        elif r < 0.92:
            # Setup / Changeover
            dur = random.randint(5, 18)
            state, code = "Setup", 2
            pieces, good, bad = 0, 0, 0
        else:
            # Micro-stop
            dur = random.randint(1, 4)
            state, code = "Micro-stop", 3
            pieces, good, bad = 0, 0, 0

        ev_end = t + datetime.timedelta(minutes=dur)
        if ev_end > next_boundary:
            ev_end = next_boundary

        reason = None
        if state == "Stopped":
            reason = random.choice([
                "Falta Material", "Fallo Sensor X", "Cambio Formato",
                "Mantenimiento Preventivo", "Error Operario"
            ])

        # Map to today's sequences based on time elapsed in the shift
        seq_id = None
        if seq_list:
            shift_duration = (SHIFT_END - SHIFT_START).total_seconds()
            elapsed = (t - SHIFT_START).total_seconds()
            seq_idx = int(elapsed / shift_duration * len(seq_list))
            seq_idx = min(max(0, seq_idx), len(seq_list) - 1)
            seq_id = seq_list[seq_idx]

        events.append({
            "state": state, "state_code": code,
            "start": t, "end": ev_end,
            "pieces": pieces, "good": good, "bad": bad, "reason": reason,
            "secuencia_id": seq_id
        })
        t = ev_end

    # Insert all events via SQL
    total_good, total_bad = 0, 0
    for ev in events:
        total_good += ev["good"]
        total_bad += ev["bad"]
        reason_val = f"'{ev['reason']}'" if ev["reason"] else "NULL"
        seq_val = f"'{ev['secuencia_id']}'" if ev.get("secuencia_id") else "NULL"
        grafana_sql(f"""
            INSERT INTO mes_machine_events
            (machine_id, state, timestamp, piece_count, good_count, bad_count, reason_code, source, created_at, secuencia_id)
            VALUES ('{MACHINE_ID}', '{ev["state"]}', '{ev["start"].strftime(FMT)}',
                    {ev["pieces"]}, {ev["good"]}, {ev["bad"]}, {reason_val}, 'seed', GETDATE(), {seq_val})
        """)

    print(f"  [OK] Inserted {len(events)} machine events")
    print(f"       Total Good: {total_good}, Total Bad: {total_bad}")
    return events, total_good, total_bad


def seed_stop_reasons(events):
    """Insert stop reason records from the events."""
    stop_events = [e for e in events if e["state"] == "Stopped"]
    for ev in stop_events:
        dur = int((ev["end"] - ev["start"]).total_seconds())
        grafana_sql(f"""
            INSERT INTO mes_stop_reasons (machine_id, reason, duration_s, start_time, end_time)
            VALUES ('{MACHINE_ID}', '{ev["reason"]}', {dur},
                    '{ev["start"].strftime(FMT)}', '{ev["end"].strftime(FMT)}')
        """)
    print(f"  [OK] Inserted {len(stop_events)} stop reason records")


def seed_reject_reasons(total_bad):
    """Insert reject reasons distributed across categories."""
    reasons = {"Medida": 0, "Tacha": 0, "Color": 0}
    remaining = total_bad
    for i, reason in enumerate(reasons):
        if i == len(reasons) - 1:
            reasons[reason] = remaining
        else:
            qty = random.randint(0, remaining)
            reasons[reason] = qty
            remaining -= qty

    # Ensure at least some rejects for demo
    if total_bad < 5:
        reasons = {"Medida": 14, "Tacha": 10, "Color": 7}

    for reason, qty in reasons.items():
        if qty > 0:
            offset = random.randint(0, int((SHIFT_END - SHIFT_START).total_seconds()) - 60)
            ts = SHIFT_START + datetime.timedelta(seconds=offset)
            grafana_sql(f"""
                INSERT INTO mes_reject_reasons (machine_id, reason, quantity, timestamp)
                VALUES ('{MACHINE_ID}', '{reason}', {qty}, '{ts.strftime(FMT)}')
            """)
    print(f"  [OK] Inserted reject reasons: {reasons}")


def seed_oee_snapshots(events, total_good, total_bad):
    """Insert OEE snapshot every 10 minutes."""
    total_pieces = total_good + total_bad
    now = datetime.datetime.now()
    end = min(SHIFT_END, now)
    shift_seconds = (end - SHIFT_START).total_seconds()
    break_seconds = min((BREAK_END - BREAK_START).total_seconds(),
                        max(0, (min(end, BREAK_END) - BREAK_START).total_seconds()))
    planned_time = shift_seconds - break_seconds

    run_time = sum(
        (e["end"] - e["start"]).total_seconds()
        for e in events if e["state"] == "Running"
    )

    ideal_cycle_time = 27  # seconds per piece
    avail = (run_time / planned_time) * 100 if planned_time > 0 else 0
    perf = (total_pieces * ideal_cycle_time / run_time) * 100 if run_time > 0 else 0
    perf = min(perf, 100)  # cap at 100%
    qual = (total_good / total_pieces) * 100 if total_pieces > 0 else 0
    oee = (avail / 100) * (perf / 100) * (qual / 100) * 100

    print(f"  [INFO] Actual OEE: {oee:.1f}% (A={avail:.1f}%, P={perf:.1f}%, Q={qual:.1f}%)")
    print(f"  [INFO] Planned: {planned_time:.0f}s, Run: {run_time:.0f}s, Pieces: {total_pieces}")

    # Snapshots every 10 min
    t = SHIFT_START + datetime.timedelta(minutes=10)
    count = 0
    while t <= end:
        elapsed = (t - SHIFT_START).total_seconds()
        progress = elapsed / shift_seconds

        noise_a = random.uniform(-1.5, 1.5)
        noise_p = random.uniform(-1, 1)
        noise_q = random.uniform(-0.2, 0.2)

        snap_avail = min(100, max(0, avail + noise_a))
        snap_perf = min(100, max(0, perf + noise_p))
        snap_qual = min(100, max(0, qual + noise_q))
        snap_oee = (snap_avail / 100) * (snap_perf / 100) * (snap_qual / 100) * 100

        cum_pieces = int(total_pieces * progress)
        cum_good = int(total_good * progress)

        grafana_sql(f"""
            INSERT INTO mes_oee_snapshots
            (machine_id, ts, window_minutes, availability, performance, quality, oee,
             planned_time_s, run_time_s, total_pieces, good_pieces, ideal_cycle_time_s, shift_label)
            VALUES ('{MACHINE_ID}', '{t.strftime(FMT)}', 10,
                    {snap_avail:.2f}, {snap_perf:.2f}, {snap_qual:.2f}, {snap_oee:.2f},
                    {elapsed:.0f}, {run_time * progress:.0f}, {cum_pieces}, {cum_good},
                    {ideal_cycle_time}, 'T1')
        """)
        count += 1
        t += datetime.timedelta(minutes=10)

    print(f"  [OK] Inserted {count} OEE snapshots")
    return avail, perf, qual, oee, total_pieces


def update_machine_status(total_good, total_bad):
    """Update current machine status."""
    total = total_good + total_bad
    grafana_sql(f"""
        UPDATE mes_machine_status
        SET state = 'Running', connected = 1, last_event_ts = GETDATE(),
            piece_count = {total}, good_count = {total_good}, bad_count = {total_bad},
            updated_at = GETDATE()
        WHERE machine_id = '{MACHINE_ID}'
    """)
    print("  [OK] Updated machine status")


def ensure_today_setup():
    """Ensure today is set up in CALENDARIO_LABORAL and JAULA_ERP."""
    active_date_str = TODAY.strftime("%Y-%m-%d")
    active_date_erp = TODAY.strftime("%Y%m%d")

    print(f"  [INFO] Ensuring calendar entry for today ({active_date_str})...")
    # Check if entry exists
    cal_res = grafana_sql(f"SELECT COUNT(*) as cnt FROM dbo.CALENDARIO_LABORAL WHERE Fecha = '{active_date_str}'")
    cal_count = 0
    try:
        if cal_res and "results" in cal_res:
            frames = cal_res["results"]["A"]["frames"]
            if frames and len(frames) > 0:
                data = frames[0]["data"]
                if data and "values" in data and len(data["values"]) > 0:
                    cal_count = data["values"][0][0]
    except Exception as e:
        print(f"  [WARNING] Could not parse CALENDARIO_LABORAL check results: {e}")

    if cal_count > 0:
        # Update existing
        grafana_sql(f"UPDATE dbo.CALENDARIO_LABORAL SET Laborable = 1, Cant_A_Fabricar = 18, Tipo_Dia = 'Laborable' WHERE Fecha = '{active_date_str}'")
        print(f"  [OK] Updated today's calendar entry to Laborable=True, Cant=18")
    else:
        # Insert new
        grafana_sql(f"INSERT INTO dbo.CALENDARIO_LABORAL (Fecha, Tipo_Dia, Laborable, Cant_A_Fabricar) VALUES ('{active_date_str}', 'Laborable', 1, 18)")
        print(f"  [OK] Inserted today's calendar entry as Laborable=True, Cant=18")

    print(f"  [INFO] Ensuring sequences in JAULA_ERP for today ({active_date_erp})...")
    erp_res = grafana_sql(f"SELECT COUNT(*) as cnt FROM dbo.JAULA_ERP WHERE fecha_montaje = '{active_date_erp}'")
    erp_count = 0
    try:
        if erp_res and "results" in erp_res:
            frames = erp_res["results"]["A"]["frames"]
            if frames and len(frames) > 0:
                data = frames[0]["data"]
                if data and "values" in data and len(data["values"]) > 0:
                    erp_count = data["values"][0][0]
    except Exception as e:
        print(f"  [WARNING] Could not parse JAULA_ERP check results: {e}")

    if erp_count > 0:
        print(f"  [OK] Found {erp_count} sequences in JAULA_ERP for today")
        return

    # Find latest date in JAULA_ERP
    print("  [INFO] No sequences found for today in JAULA_ERP. Copying from latest available date...")
    latest_res = grafana_sql(f"SELECT TOP 1 fecha_montaje FROM dbo.JAULA_ERP WHERE fecha_montaje < '{active_date_erp}' ORDER BY fecha_montaje DESC")
    latest_date = None
    try:
        if latest_res and "results" in latest_res:
            frames = latest_res["results"]["A"]["frames"]
            if frames and len(frames) > 0:
                data = frames[0]["data"]
                if data and "values" in data and len(data["values"]) > 0:
                    latest_date = data["values"][0][0]
    except Exception as e:
        print(f"  [WARNING] Could not parse latest JAULA_ERP date: {e}")

    if not latest_date:
        latest_date = "20260619"  # Fallback

    print(f"  [INFO] Copying sequences from {latest_date} to {active_date_erp}...")
    insert_query = f"""
        INSERT INTO dbo.JAULA_ERP (
            fecha_montaje, secuencia, modelo, bastidor, mastil, altura_max_interm,
            capac_interm_1, capac_interm_2, capac_interm_3, tpo_elevac_min, tpo_elevac_max,
            tpo_descenso_min, tpo_descenso_max, tpo_incl_adel_max, tpo_incl_atras_max,
            tpo_elev_min_scarga, tpo_elev_max_scarga, tpo_desc_min_scarga, tpo_desc_max_scarga,
            peso_pruebas, fecha_importacion
        )
        SELECT 
            '{active_date_erp}', secuencia, modelo, CAST(bastidor AS VARCHAR(18)) + '_' + SUBSTRING('{active_date_erp}', 5, 4), mastil, altura_max_interm,
            capac_interm_1, capac_interm_2, capac_interm_3, tpo_elevac_min, tpo_elevac_max,
            tpo_descenso_min, tpo_descenso_max, tpo_incl_adel_max, tpo_incl_atras_max,
            tpo_elev_min_scarga, tpo_elev_max_scarga, tpo_desc_min_scarga, tpo_desc_max_scarga,
            peso_pruebas, GETDATE()
        FROM dbo.JAULA_ERP
        WHERE fecha_montaje = '{latest_date}'
    """
    grafana_sql(insert_query)
    print(f"  [OK] Sequences copied successfully to today ({active_date_erp})")


def main():
    print("=" * 60)
    print("  OEE Demo Data Seeder (via Grafana API)")
    print(f"  Shift: {SHIFT_START.strftime('%H:%M')} - {SHIFT_END.strftime('%H:%M')}")
    print(f"  Break: {BREAK_START.strftime('%H:%M')} - {BREAK_END.strftime('%H:%M')}")
    print("=" * 60)

    print("\n[1/7] Ensuring helper tables...")
    ensure_tables()

    print("\n[1.5/7] Ensuring today's setup in DB...")
    ensure_today_setup()

    print("\n[2/7] Clearing old demo data...")
    clear_demo_data()

    print("\n[3/7] Seeding machine events...")
    events, total_good, total_bad = seed_machine_events()

    print("\n[4/7] Seeding stop reasons (Pareto)...")
    seed_stop_reasons(events)

    print("\n[5/7] Seeding reject reasons (Donut)...")
    seed_reject_reasons(total_bad)

    print("\n[6/7] Seeding OEE snapshots...")
    avail, perf, qual, oee, total = seed_oee_snapshots(events, total_good, total_bad)

    print("\n[7/7] Updating machine status...")
    update_machine_status(total_good, total_bad)

    print("\n" + "=" * 60)
    print("  DONE! Summary:")
    print(f"    OEE: {oee:.1f}%  |  Availability: {avail:.1f}%")
    print(f"    Performance: {perf:.1f}%  |  Quality: {qual:.1f}%")
    print(f"    Total: {total}  |  Good: {total_good}  |  Bad: {total_bad}")
    print("=" * 60)


if __name__ == "__main__":
    main()
