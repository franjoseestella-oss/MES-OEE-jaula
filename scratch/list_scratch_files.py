import os
import datetime

scratch_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\scratch"
files_info = []
for f in os.listdir(scratch_dir):
    path = os.path.join(scratch_dir, f)
    if os.path.isfile(path):
        stat = os.stat(path)
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        files_info.append((f, stat.st_size, mtime))

files_info.sort(key=lambda x: x[2], reverse=True)
for name, size, mtime in files_info:
    print(f"{name:50} | {size:10} bytes | {mtime}")
