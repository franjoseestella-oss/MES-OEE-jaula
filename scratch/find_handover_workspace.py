import os

base_dir = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE"
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if "handover" in f.lower():
            print(os.path.join(root, f))
