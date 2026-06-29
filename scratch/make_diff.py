import difflib

with open("scratch/plan_live_sanitized.json", "r", encoding="utf-8") as f:
    live = f.readlines()
with open("scratch/plan_local_sanitized.json", "r", encoding="utf-8") as f:
    local = f.readlines()

diff = difflib.unified_diff(live, local, fromfile="live", tofile="local")

with open("scratch/plan_diff.patch", "w", encoding="utf-8") as f:
    f.writelines(diff)

print("Diff saved to scratch/plan_diff.patch")
