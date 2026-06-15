"""
Complete JS patch for Grafana configFromData handlers.

Current state in JS (position ~2908129):
  {key:"threshold1", targetProperty:"thresholds", processor:(w,z)=>{
    const Z=(0,cn.t)(w);
    if(!isNaN(Z))return z.thresholds
      ?(z.thresholds.steps.push({value:Z,color:"red"}),z.thresholds)
      :(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)
  }},
  {key:"mappings.value",...}   <-- next handler, no threshold2 handler exists!

Desired state:
  threshold1: set z.min = Z * 0.85, create [{-inf:red},{Z:green}]
  threshold2: set z.max = Z * 1.15, push {Z:red}  (final: [{-inf:red},{Min:green},{Max:red}])
"""
import sys, shutil, re
sys.stdout.reconfigure(encoding='utf-8')

JS_SRC  = 'scratch/5017.aaaa340b86e350c74a1f.js'
JS_DST  = 'scratch/5017.aaaa340b86e350c74a1f.js'  # overwrite in place

print("Reading JS...")
with open(JS_SRC, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# ─── 1. Find the EXACT threshold1 handler string ─────────────────────────────
# We'll match the exact pattern in the minified code

OLD_TH1 = (
    '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>'
    '{const Z=(0,cn.t)(w);if(!isNaN(Z))return z.thresholds'
    '?(z.thresholds.steps.push({value:Z,color:"red"}),z.thresholds)'
    ':(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"}'
    ',{value:Z,color:"green"}]},z.thresholds)}}'
)

if OLD_TH1 not in content:
    print("ERROR: Could not find threshold1 handler to patch!")
    print("Searching for partial match...")
    idx = content.find('{key:"threshold1"')
    if idx > 0:
        print(f"Found at {idx}:")
        print(repr(content[idx:idx+300]))
    sys.exit(1)

print("Found threshold1 handler ✓")

# ─── 2. Build the replacement ─────────────────────────────────────────────────
# threshold1: sets min scale + base thresholds [red, green@Min]
# threshold2: sets max scale + appends red@Max to thresholds

NEW_HANDLERS = (
    # threshold1: fix — also set z.min to 85% of Min value
    '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{'
    'const Z=(0,cn.t)(w);'
    'if(!isNaN(Z)){'
    'z.min=parseFloat((Z*0.85).toFixed(3));'  # gauge scale min = 85% of Min threshold
    'return z.thresholds'
    '?(z.thresholds.steps.push({value:Z,color:"green"}),z.thresholds)'
    ':(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)'
    '}}}'
    # threshold2: NEW — also set z.max to 115% of Max value
    ',{key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{'
    'const Z=(0,cn.t)(w);'
    'if(!isNaN(Z)){'
    'z.max=parseFloat((Z*1.15).toFixed(3));'  # gauge scale max = 115% of Max threshold
    'if(z.thresholds){'
    'z.thresholds.steps.push({value:Z,color:"red"});'
    'return z.thresholds'
    '}'
    'return z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"red"}]},z.thresholds'
    '}}}'
)

# ─── 3. Apply patch ───────────────────────────────────────────────────────────
patched = content.replace(OLD_TH1, NEW_HANDLERS, 1)

if patched == content:
    print("ERROR: Replacement failed (content unchanged)!")
    sys.exit(1)

# Verify
count_th1 = patched.count('"threshold1"')
count_th2 = patched.count('"threshold2"')
print(f"After patch: 'threshold1' found {count_th1} times, 'threshold2' found {count_th2} times")

# Check we added threshold2 as a handler key
if '{key:"threshold2"' not in patched:
    print("ERROR: threshold2 handler not injected!")
    sys.exit(1)

print("threshold2 handler injected ✓")

# ─── 4. Save ─────────────────────────────────────────────────────────────────
with open(JS_DST, 'w', encoding='utf-8') as f:
    f.write(patched)

print(f"Saved patched JS to {JS_DST}")
print(f"File size: {len(patched):,} bytes")

# ─── 5. Quick sanity check: show the new handler area ─────────────────────────
idx = patched.find('{key:"threshold1"')
print("\n=== Patched handler (first 600 chars) ===")
print(patched[idx:idx+600])
