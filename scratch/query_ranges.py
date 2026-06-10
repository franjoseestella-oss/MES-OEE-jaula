"""Query the latest values and configured ranges from the DB."""
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run(
    ['docker', 'exec', 'mes_sqlserver', '/opt/mssql-tools18/bin/sqlcmd',
     '-S', 'localhost', '-U', 'sa', '-P', 'MesPassword123!', '-C',
     '-Q', '''SELECT TOP 1 
         TIEMPO_ELEVACION_MEDIDO_SINCARGA, TIEMPO_ELEVACION_MIN_SINCARGA, TIEMPO_ELEVACION_MAX_SINCARGA,
         TIEMPO_DESCENSO_MEDIDO_SINCARGA, TIEMPO_DESCENSO_MIN_SINCARGA, TIEMPO_DESCENSO_MAX_SINCARGA,
         TIEMPO_ELEVACION_MEDIDO_CARGA, TIEMPO_ELEVACION_MIN_CARGA, TIEMPO_ELEVACION_MAX_CARGA,
         TIEMPO_DESCENSO_MEDIDO_CARGA, TIEMPO_DESCENSO_MIN_CARGA, TIEMPO_DESCENSO_MAX_CARGA
     FROM LOG_TABLA ORDER BY fecha_creacion DESC'''],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("Latest values from DB:")
print(result.stdout[:3000])
print(result.stderr[:500])
