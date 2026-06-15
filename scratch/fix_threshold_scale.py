"""
Fix the threshold1/threshold2 processor in the patched JS bundle.

Current (WRONG):
  threshold1: z.min = Z * 0.85  → overrides the fixed 1-6 scale
  threshold2: z.max = Z * 1.15  → overrides the fixed 1-6 scale

Correct (WANTED):
  threshold1: ONLY sets a green step at Min value (does NOT touch z.min)
  threshold2: ONLY sets a red step at Max value  (does NOT touch z.max)

This way:
  - Fixed scale (1-6) stays from fieldConfig.defaults.min/max
  - Color zones: red (1→Min), green (Min→Max), red (Max→6)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

js_path = r'scratch\5017.aaaa340b86e350c74a1f.js'
print(f"Reading {js_path}...")
with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"Total chars: {len(content):,}")

# ─── Find and replace threshold1 processor ────────────────────────────────────
# Current (WRONG) threshold1 handler - sets z.min:
OLD_T1 = (
    '{key:"threshold1",targetProperty:"thresholds",'
    'processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))'
    '{z.min=parseFloat((Z*0.85).toFixed(3));'
    'return z.thresholds?'
    '(z.thresholds.steps.push({value:Z,color:"green"}),z.thresholds):'
    '(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)}}}'
)

# New (CORRECT) threshold1 handler - only adds green step, does NOT set z.min:
NEW_T1 = (
    '{key:"threshold1",targetProperty:"thresholds",'
    'processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))'
    '{return z.thresholds?'
    '(z.thresholds.steps.push({value:Z,color:"green"}),z.thresholds):'
    '(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)}}}'
)

# ─── Find and replace threshold2 processor ────────────────────────────────────
# Current (WRONG) threshold2 handler - sets z.max:
OLD_T2 = (
    '{key:"threshold2",targetProperty:"thresholds",'
    'processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))'
    '{z.max=parseFloat((Z*1.15).toFixed(3));'
    'if(z.thresholds){z.thresholds.steps.push({value:Z,color:"red"});return z.thresholds}'
    'return z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"red"}]},z.thresholds}}}'
)

# New (CORRECT) threshold2 handler - only adds red step, does NOT set z.max:
NEW_T2 = (
    '{key:"threshold2",targetProperty:"thresholds",'
    'processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))'
    '{if(z.thresholds){z.thresholds.steps.push({value:Z,color:"red"});return z.thresholds}'
    'return z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"red"}]},z.thresholds}}}'
)

# ─── Apply patches ────────────────────────────────────────────────────────────
if OLD_T1 not in content:
    print("ERROR: OLD_T1 not found! Dumping nearby context...")
    idx = content.find('key:"threshold1"')
    if idx != -1:
        print(repr(content[idx:idx+400]))
    else:
        print("threshold1 key not found at all!")
else:
    content = content.replace(OLD_T1, NEW_T1, 1)
    print("✓ threshold1 processor patched (removed z.min override)")

if OLD_T2 not in content:
    print("ERROR: OLD_T2 not found! Dumping nearby context...")
    idx = content.find('key:"threshold2"')
    if idx != -1:
        print(repr(content[idx:idx+400]))
    else:
        print("threshold2 key not found at all!")
else:
    content = content.replace(OLD_T2, NEW_T2, 1)
    print("✓ threshold2 processor patched (removed z.max override)")

# ─── Write patched file ───────────────────────────────────────────────────────
out_path = r'scratch\5017.aaaa340b86e350c74a1f.js'
with open(out_path, 'w', encoding='utf-8', errors='replace') as f:
    f.write(content)
print(f"✓ Written to {out_path}")
print("\nNext: docker cp the file into the container and restart Grafana.")
