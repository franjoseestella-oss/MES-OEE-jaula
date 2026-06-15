import sys

JS_FILE = 'scratch/5017.aaaa340b86e350c74a1f.js'

with open(JS_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Let's locate our patched threshold1 and threshold2 handlers:
# '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z)){z.min=parseFloat((Z*0.85).toFixed(3));return z.thresholds?(z.thresholds.steps.push({value:Z,color:"green"}),z.thresholds):(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)}}}'
# ',{key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z)){z.max=parseFloat((Z*1.15).toFixed(3));if(z.thresholds){z.thresholds.steps.push({value:Z,color:"red"});return z.thresholds}return z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"red"}]},z.thresholds}}}'

target_th1 = 'key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{'
target_th2 = 'key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{'

if target_th1 not in content or target_th2 not in content:
    print("ERROR: Could not find threshold1 or threshold2 key in JS file.")
    sys.exit(1)

# Let's replace the processors with logged versions:
logged_th1_proc = (
    'key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{'
    'const Z=(0,cn.t)(w);'
    'console.log("TH1 CALLED: Z =", Z, "z.min before =", z.min, "z.thresholds steps =", z.thresholds ? JSON.stringify(z.thresholds.steps) : "none");'
    'if(!isNaN(Z)){'
    'z.min=parseFloat((Z*0.85).toFixed(3));'
    'let res = z.thresholds'
    '?(z.thresholds.steps.push({value:Z,color:"green"}),z.thresholds)'
    ':(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds);'
    'console.log("TH1 RESULT steps =", JSON.stringify(z.thresholds.steps), "z.min =", z.min);'
    'return res;'
    '}'
    '}'
)

logged_th2_proc = (
    'key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{'
    'const Z=(0,cn.t)(w);'
    'console.log("TH2 CALLED: Z =", Z, "z.max before =", z.max, "z.thresholds steps =", z.thresholds ? JSON.stringify(z.thresholds.steps) : "none");'
    'if(!isNaN(Z)){'
    'z.max=parseFloat((Z*1.15).toFixed(3));'
    'let res;'
    'if(z.thresholds){'
    'z.thresholds.steps.push({value:Z,color:"red"});'
    'res = z.thresholds;'
    '} else {'
    'res = z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"red"}]},z.thresholds;'
    '}'
    'console.log("TH2 RESULT steps =", JSON.stringify(z.thresholds.steps), "z.max =", z.max);'
    'return res;'
    '}'
    '}'
)

# Apply replacement (be careful, we want to replace the whole handler block up to '}}}')
# Let's locate the exact handler blocks:
# '{key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{...}}}'
# and ',{key:"threshold2",targetProperty:"thresholds",processor:(w,z)=>{...}}}'

# We can find the start of threshold1 and search for the closing bracket '}}}'
idx_th1 = content.find('{key:"threshold1"')
idx_end_th1 = content.find('}}}', idx_th1) + 3
old_block_th1 = content[idx_th1:idx_end_th1]

idx_th2 = content.find('{key:"threshold2"')
idx_end_th2 = content.find('}}}', idx_th2) + 3
old_block_th2 = content[idx_th2:idx_end_th2]

print("Original TH1 block:")
print(old_block_th1)
print("\nOriginal TH2 block:")
print(old_block_th2)

new_block_th1 = '{' + logged_th1_proc + '}'
new_block_th2 = '{' + logged_th2_proc + '}'

patched = content.replace(old_block_th1, new_block_th1, 1).replace(old_block_th2, new_block_th2, 1)

with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(patched)

print("\n✓ Injected console logs successfully!")
