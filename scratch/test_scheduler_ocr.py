import sys
import os
import shutil
from pathlib import Path

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database.session import get_db
from models.events import OeeSnapshot
from oee.scheduler import run_snapshot, find_hmi_screenshots

def test():
    print("=== STARTING OCR SCHEDULER TEST ===")
    
    # 1. Check if screenshots are present
    project_root = Path(__file__).resolve().parent.parent
    p1 = project_root / "media_user_1.png"
    p2 = project_root / "media_user_2.png"
    
    # Check if they are in archive_screenshots and copy them back if they aren't in the root
    archive_dir = project_root / "archive_screenshots"
    if not p1.exists() or not p2.exists():
        print("Screenshots not found in root. Checking archive...")
        if archive_dir.exists():
            archived_p1 = list(archive_dir.glob("media_user_1_*.png"))
            archived_p2 = list(archive_dir.glob("media_user_2_*.png"))
            if archived_p1 and archived_p2:
                # Copy the most recent ones back to root
                archived_p1.sort(key=lambda x: x.stat().st_mtime)
                archived_p2.sort(key=lambda x: x.stat().st_mtime)
                shutil.copy(str(archived_p1[-1]), str(p1))
                shutil.copy(str(archived_p2[-1]), str(p2))
                print(f"Restored screenshots from archive: {archived_p1[-1].name}, {archived_p2[-1].name}")
            else:
                print("No archived screenshots found to restore!")
        else:
            print("No archive directory exists yet.")
            
    # Verify we have images to test with
    found = find_hmi_screenshots()
    print("Found HMI screenshots for test:", found)
    if not found:
        print("ERROR: No HMI screenshots available for testing.")
        return
        
    # Get last snapshot ID before running
    with get_db() as db:
        last_snap_before = db.query(OeeSnapshot).order_by(OeeSnapshot.ts.desc()).first()
        before_id = last_snap_before.id if last_snap_before else 0
        print(f"Latest Snapshot ID before test: {before_id}")
        
    # 2. Run snapshot
    print("Running run_snapshot()...")
    run_snapshot()
    
    # 3. Check if files were moved to archive
    print("Checking if files were moved...")
    if p1.exists() or p2.exists():
        print("WARNING: Original screenshot files still exist in root!")
    else:
        print("SUCCESS: Original screenshots removed from root.")
        
    if archive_dir.exists():
        archived_files = list(archive_dir.glob("media_user_*"))
        print(f"Archived files in {archive_dir}:")
        for f in archived_files:
            print(f" - {f.name}")
    else:
        print("ERROR: Archive directory was not created!")
        
    # 4. Verify database update
    print("Verifying database snapshot insertion...")
    with get_db() as db:
        snaps = db.query(OeeSnapshot).filter(OeeSnapshot.id > before_id).order_by(OeeSnapshot.ts.desc()).all()
        if snaps:
            print(f"SUCCESS: Found {len(snaps)} new snapshots in database:")
            for s in snaps:
                print(f"ID: {s.id} | Machine: {s.machine_id} | TS: {s.ts} | OEE: {s.oee} | A: {s.availability} | P: {s.performance} | Q: {s.quality} | Good/Total: {s.good_pieces}/{s.total_pieces} | Run/Planned: {s.run_time_s}/{s.planned_time_s} | Turno: {s.shift_label}")
        else:
            print("ERROR: No new snapshots were created in the database!")

if __name__ == "__main__":
    test()
