import os
import zipfile
from pathlib import Path

def main():
    scratch_dir = Path(__file__).resolve().parent
    archive_dir = scratch_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    zip_path = archive_dir / "legacy_scratch_files.zip"
    
    # Files to exclude from archive/deletion
    exclude_files = {
        "archive_legacy.py",
        "view_snapshots.py",  # Keep this as it's a helpful diagnostic script for the user
    }
    
    print(f"Archiving legacy files from {scratch_dir} to {zip_path}...")
    
    files_to_archive = []
    for item in scratch_dir.iterdir():
        if item.is_file() and item.name not in exclude_files:
            # We want to archive Python scripts, txt files, etc.
            if item.suffix in [".py", ".txt", ".png", ".log"]:
                files_to_archive.append(item)
                
    if not files_to_archive:
        print("No legacy files to archive.")
        return
        
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_archive:
            print(f"Adding: {file_path.name}")
            zipf.write(file_path, arcname=file_path.name)
            
    print("Archive created successfully. Deleting original files...")
    for file_path in files_to_archive:
        try:
            file_path.unlink()
            print(f"Deleted: {file_path.name}")
        except Exception as e:
            print(f"Failed to delete {file_path.name}: {e}")
            
    print("Done!")

if __name__ == "__main__":
    main()
