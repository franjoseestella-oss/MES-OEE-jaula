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

        events.append({
            "state": state, "state_code": code,
            "start": t, "end": ev_end,
            "pieces": pieces, "good": good, "bad": bad, "reason": reason
        })
        t = ev_end

    # Insert all events via SQL
    total_good, total_bad = 0, 0
    for ev in events:
        total_good += ev["good"]
        total_bad += ev["bad"]
        reason_val = f"'{ev['reason']}'" if ev["reason"] else "NULL"
        grafana_sql(f"""
            INSERT INTO mes_machine_events
            (machine_id, state, timestamp, piece_count, good_count, bad_count, reason_code, source, created_at)
            VALUES ('{MACHINE_ID}', '{ev["state"]}', '{ev["start"].strftime(FMT)}',
                    {ev["pieces"]}, {ev["good"]}, {ev["bad"]}, {reason_val}, 'seed', GETDATE())
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


def main():
    print("=" * 60)
    print("  OEE Demo Data Seeder (via Grafana API)")
    print(f"  Shift: {SHIFT_START.strftime('%H:%M')} - {SHIFT_END.strftime('%H:%M')}")
    print(f"  Break: {BREAK_START.strftime('%H:%M')} - {BREAK_END.strftime('%H:%M')}")
    print("=" * 60)

    print("\n[1/7] Ensuring helper tables...")
    ensure_tables()

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
