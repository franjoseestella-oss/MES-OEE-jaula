"""Apply the correct threshold1/threshold2 patch to the JS file."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/5017_patched.js', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"Original size: {len(content):,}")

# EXACT old threshold1 handler (taken from the repr output above, decoded):
OLD_T1 = '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))return z.thresholds||(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"green"}]}),z.thresholds.steps.push({value:Z,color:"red"}),z.thresholds}}'

# NEW threshold1: starts RED, goes GREEN at min value
NEW_T1 = '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z)){z.thresholds||(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"#E32636"}]});z.thresholds.steps=[{value:-1/0,color:"#E32636"},{value:Z,color:"#2FD06A"}];return z.thresholds}}}'

# NEW threshold2: adds RED step at max value (appended after threshold1 in the An array)
NEW_T2 = ',{key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z)){if(!z.thresholds){z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"#E32636"}]};}if(!z.thresholds.steps.some(s=>s.value===Z)){z.thresholds.steps.push({value:Z,color:"#E32636"});}return z.thresholds}}}'

if OLD_T1 in content:
    print("Found OLD threshold1 - replacing...")
    new_content = content.replace(OLD_T1, NEW_T1 + NEW_T2, 1)
    print(f"New size: {len(new_content):,}")
    
    # Verify the replacement
    if '{key:"threshold1"' in new_content and '{key:"threshold2"' in new_content:
        print("Both threshold1 and threshold2 are now in the file")
    
    with open('scratch/5017_newpatch.js', 'w', encoding='utf-8', errors='replace') as f:
        f.write(new_content)
    print("Written to scratch/5017_newpatch.js")
else:
    print("ERROR: Could not find OLD threshold1 string!")
    # Try to find partial match
    idx = content.find('{key:"threshold1"')
    if idx >= 0:
        print("Nearby content (repr):")
        print(repr(content[idx:idx+300]))
