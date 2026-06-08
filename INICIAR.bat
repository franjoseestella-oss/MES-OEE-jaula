@echo off
title LOGISNEXT — MES/OEE
cd /d "%~dp0"
chcp 65001 >nul

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   LOGISNEXT  ·  MES / OEE  ·  Arranque             ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  [1]  Arranque completo  (Docker: backend + Grafana + MQTT)
echo  [2]  Solo web local     (Python directo, sin Docker)
echo  [3]  Ver diseno del sistema  (navegador, sin instalar nada)
echo  [0]  Salir
echo.
set /p OPCION="  Elige opcion: "

if "%OPCION%"=="1" goto DOCKER
if "%OPCION%"=="2" goto LOCAL
if "%OPCION%"=="3" goto DISEÑO
if "%OPCION%"=="0" exit /b 0
goto FIN

:DOCKER
echo.
echo  Iniciando con Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Docker no encontrado. Instala Docker Desktop.
        pause & exit /b 1
    )
    docker-compose up --build -d
) else (
    docker compose up --build -d
)
echo.
echo  Esperando que el backend este listo en localhost:8000 ...
timeout /t 8 /nobreak >nul
start "" "http://localhost:8000"
timeout /t 2 /nobreak >nul
start "" "http://localhost:3010"
echo.
echo  Aplicacion abierta:
echo    Chatbot / API  →  http://localhost:8000
echo    Grafana        →  http://localhost:3010
echo.
goto FIN

:LOCAL
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no encontrado. Instala Python 3.11+.
    pause & exit /b 1
)
cd backend
echo  Instalando dependencias (primera vez puede tardar)...
pip install fastapi uvicorn[standard] paho-mqtt pyodbc SQLAlchemy pydantic pydantic-settings anthropic apscheduler jinja2 markdown >nul 2>&1
echo  Arrancando backend en http://localhost:8000 ...
start "" "http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
goto FIN

:DISEÑO
start "" "%~dp0design_overview.html"
goto FIN

:FIN
echo.
pause
