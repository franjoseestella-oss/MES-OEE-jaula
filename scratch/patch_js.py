original = 'key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))return z.thresholds||(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"green"}]}),z.thresholds.steps.push({value:Z,color:"red"}),z.thresholds}'
replacement = 'key:"threshold1",targetProperty:"thresholds",processor:(w,z)=>{const Z=(0,cn.t)(w);if(!isNaN(Z))return z.thresholds?(z.thresholds.steps.push({value:Z,color:"red"}),z.thresholds):(z.thresholds={mode:vn.O.Absolute,steps:[{value:-1/0,color:"red"},{value:Z,color:"green"}]},z.thresholds)}'

with open("scratch/5017.aaaa340b86e350c74a1e.js", "r", encoding="utf-8") as f:
    content = f.read()

if original in content:
    print("Found original string!")
    new_content = content.replace(original, replacement)
    with open("scratch/5017.aaaa340b86e350c74a1e.js", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully patched local file!")
else:
    print("Could not find the original string in the local file.")
