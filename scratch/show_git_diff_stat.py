import subprocess

res = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
print(res.stdout)
