#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  LOGISNEXT — MES / OEE  ·  Script de Arranque
  Uso:  python iniciar.py
        doble clic en Windows
═══════════════════════════════════════════════════════════════════════

Funcionalidades:
  1. Arranque completo con Docker (backend + Grafana + MQTT)
  2. Arranque local sin Docker (Python + uvicorn directo)
  3. Ver diseño del sistema (abre design_overview.html)
  4. Ver logs en tiempo real de los contenedores
  5. Detener todos los servicios Docker
"""

import os
import sys
import shutil
import subprocess
import time
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────
#  Colores ANSI (se habilitan en Windows automáticamente)
# ─────────────────────────────────────────────────────────────────────
if sys.platform == "win32":
    os.system("color")  # habilitar secuencias ANSI en cmd/PowerShell

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ─────────────────────────────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent
ENV_FILE      = ROOT / ".env"
ENV_EXAMPLE   = ROOT / ".env.example"
COMPOSE_FILE  = ROOT / "docker-compose.yml"
BACKEND_DIR   = ROOT / "backend"
DESIGN_HTML   = ROOT / "design_overview.html"

URLS = {
    "Backend / API":  "http://localhost:8000",
    "API Docs":       "http://localhost:8000/docs",
    "Chatbot":        "http://localhost:8000",
    "Grafana":        "http://localhost:3010",
}

HEALTH_URL     = "http://localhost:8000/health"
WAIT_TIMEOUT   = 90   # segundos máximos de espera
POLL_INTERVAL  = 2

VERSION = "2.0.0"


# ═════════════════════════════════════════════════════════════════════
#  Funciones de impresión con formato
# ═════════════════════════════════════════════════════════════════════

def banner():
    print(f"""
{CYAN}{BOLD}
  ╔════════════════════════════════════════════════════════════════╗
  ║                                                                ║
  ║   ██╗      ██████╗  ██████╗ ██╗███████╗███╗   ██╗███████╗     ║
  ║   ██║     ██╔═══██╗██╔════╝ ██║██╔════╝████╗  ██║██╔════╝     ║
  ║   ██║     ██║   ██║██║  ███╗██║███████╗██╔██╗ ██║█████╗       ║
  ║   ██║     ██║   ██║██║   ██║██║╚════██║██║╚██╗██║██╔══╝       ║
  ║   ███████╗╚██████╔╝╚██████╔╝██║███████║██║ ╚████║███████╗     ║
  ║   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝     ║
  ║                                                                ║
  ║        {WHITE}MES / OEE  ·  Jaula de Elevación  ·  v{VERSION}{CYAN}          ║
  ║                                                                ║
  ╚════════════════════════════════════════════════════════════════╝
{RESET}""")


def step(msg: str):
    """Mensaje de paso con flecha cyan."""
    print(f"\n  {CYAN}▶{RESET}  {WHITE}{BOLD}{msg}{RESET}")


def ok(msg: str):
    """Mensaje de éxito con checkmark verde."""
    print(f"    {GREEN}✔{RESET}  {msg}")


def warn(msg: str):
    """Mensaje de advertencia con triángulo amarillo."""
    print(f"    {YELLOW}⚠{RESET}  {YELLOW}{msg}{RESET}")


def err(msg: str):
    """Mensaje de error con X roja."""
    print(f"    {RED}✖{RESET}  {RED}{msg}{RESET}")


def info(msg: str):
    """Mensaje informativo dimmed."""
    print(f"    {DIM}{msg}{RESET}")


def die(msg: str):
    """Error fatal: muestra mensaje y sale."""
    err(msg)
    input(f"\n  {DIM}Pulsa INTRO para salir…{RESET}")
    sys.exit(1)


def separador():
    print(f"\n  {DIM}{'─' * 60}{RESET}")


# ═════════════════════════════════════════════════════════════════════
#  Utilidades
# ═════════════════════════════════════════════════════════════════════

def wait_for_http(url: str, timeout: int = WAIT_TIMEOUT) -> bool:
    """Espera hasta que una URL responda con código < 500."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status < 500:
                    return True
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    return False


def compose_cmd(*args) -> list:
    """Devuelve el comando docker compose correcto (v1 o v2)."""
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return ["docker", "compose"] + list(args)
    except Exception:
        pass
    if shutil.which("docker-compose"):
        return ["docker-compose"] + list(args)
    return ["docker", "compose"] + list(args)


# ═════════════════════════════════════════════════════════════════════
#  Verificaciones previas
# ═════════════════════════════════════════════════════════════════════

def verificar_docker() -> bool:
    """Comprueba que Docker está instalado y en marcha."""
    step("Verificando Docker…")
    if shutil.which("docker") is None:
        err("Docker no está instalado o no está en el PATH.")
        info("Instala Docker Desktop desde https://docker.com/get-started")
        return False
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            err("Docker Desktop no está en marcha.")
            info("Ábrelo y vuelve a intentarlo.")
            return False
    except subprocess.TimeoutExpired:
        err("Docker no responde (timeout).")
        return False
    ok("Docker disponible y en marcha.")
    return True


def verificar_env():
    """Comprueba y crea .env si no existe."""
    step("Verificando archivo .env…")
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            warn(".env no encontrado — se ha copiado .env.example.")
            warn("Edita .env con tus credenciales antes de continuar.")
            print()
            resp = input(f"    {YELLOW}¿Quieres editar .env ahora? (s/n): {RESET}").strip().lower()
            if resp == "s":
                if sys.platform == "win32":
                    os.startfile(str(ENV_FILE))
                else:
                    subprocess.Popen(["xdg-open", str(ENV_FILE)])
                input(f"\n    {DIM}Guarda el archivo y pulsa INTRO para continuar…{RESET}")
        else:
            die(".env.example no encontrado. Revisa la integridad del proyecto.")
    else:
        ok(".env encontrado.")


def verificar_python() -> bool:
    """Comprueba que Python 3.11+ está disponible."""
    step("Verificando Python…")
    if sys.version_info < (3, 11):
        warn(f"Python {sys.version_info.major}.{sys.version_info.minor} detectado.")
        warn("Se recomienda Python 3.11+. Puede funcionar pero no está garantizado.")
    else:
        ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✓")
    return True


# ═════════════════════════════════════════════════════════════════════
#  Servicios Docker
# ═════════════════════════════════════════════════════════════════════

def servicios_corriendo() -> bool:
    """Devuelve True si hay contenedores del compose corriendo."""
    try:
        result = subprocess.run(
            compose_cmd("ps", "--services", "--filter", "status=running"),
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def arrancar_docker():
    """Arranca todos los servicios con Docker Compose."""
    if not verificar_docker():
        return
    verificar_env()

    if not COMPOSE_FILE.exists():
        die(f"docker-compose.yml no encontrado en {ROOT}")

    step("Iniciando servicios con Docker Compose…")
    info("(Esto puede tardar 1-2 min la primera vez mientras descarga imágenes)")
    print()

    result = subprocess.run(compose_cmd("up", "--build", "-d"), cwd=ROOT)
    if result.returncode != 0:
        err("docker compose up falló. Revisa el mensaje de error arriba.")
        return

    ok("Contenedores iniciados correctamente.")

    # Esperar que el backend esté listo
    step(f"Esperando que el backend esté listo (máx. {WAIT_TIMEOUT}s)…")
    sys.stdout.write("    ")
    sys.stdout.flush()

    backend_ok = False
    deadline = time.time() + WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=3) as r:
                if r.status < 500:
                    backend_ok = True
                    break
        except Exception:
            pass
        sys.stdout.write(f"{CYAN}·{RESET}")
        sys.stdout.flush()
        time.sleep(POLL_INTERVAL)
    print()

    if backend_ok:
        ok(f"Backend listo en {HEALTH_URL}")
    else:
        warn(f"El backend no respondió en {WAIT_TIMEOUT}s. Puede que aún esté arrancando.")

    # Abrir navegador
    step("Abriendo aplicación en el navegador…")
    print()
    for nombre, url in URLS.items():
        print(f"    {GREEN}→{RESET}  {nombre:25s} {CYAN}{url}{RESET}")
    print()
    time.sleep(1)
    webbrowser.open(URLS["Backend / API"])
    time.sleep(0.5)
    webbrowser.open(URLS["Grafana"])


def arrancar_local():
    """Arranca el backend localmente sin Docker."""
    verificar_python()
    verificar_env()

    if not BACKEND_DIR.exists():
        die(f"Directorio backend/ no encontrado en {ROOT}")

    step("Instalando dependencias…")
    info("(Solo tarda la primera vez)")
    req_file = BACKEND_DIR / "requirements.txt"

    if req_file.exists():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"],
            cwd=BACKEND_DIR,
        )
    else:
        subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "fastapi", "uvicorn[standard]", "paho-mqtt", "pyodbc",
             "SQLAlchemy", "pydantic", "pydantic-settings",
             "anthropic", "apscheduler", "jinja2", "markdown", "-q"],
        )
    ok("Dependencias instaladas.")

    step("Arrancando backend en http://localhost:8000 …")
    info("Presiona Ctrl+C para detener el servidor.")
    print()

    # Abrir navegador tras un pequeño delay
    time.sleep(1)
    webbrowser.open("http://localhost:8000")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app",
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=BACKEND_DIR,
        )
    except KeyboardInterrupt:
        print(f"\n\n  {DIM}Servidor detenido.{RESET}")


def detener_servicios():
    """Detiene todos los contenedores Docker."""
    step("Deteniendo servicios Docker…")
    result = subprocess.run(compose_cmd("down"), cwd=ROOT)
    if result.returncode == 0:
        ok("Todos los servicios detenidos.")
    else:
        err("Hubo un problema al detener los servicios.")


def ver_logs():
    """Muestra los logs en tiempo real de los contenedores."""
    if not servicios_corriendo():
        warn("No hay servicios corriendo. Inícielos primero (opción 1).")
        return
    step("Mostrando logs en tiempo real (Ctrl+C para salir)...")
    try:
        subprocess.run(compose_cmd("logs", "-f", "--tail=80"), cwd=ROOT)
    except KeyboardInterrupt:
        print(f"\n  {DIM}Logs detenidos.{RESET}")


def ver_diseno():
    """Abre el archivo de diseño del sistema en el navegador."""
    if DESIGN_HTML.exists():
        step("Abriendo diseño del sistema…")
        webbrowser.open(str(DESIGN_HTML))
        ok("Archivo abierto en el navegador.")
    else:
        warn("design_overview.html no encontrado.")


def mostrar_estado():
    """Muestra el estado actual de los servicios y URLs."""
    step("Estado del sistema")
    separador()

    # Comprobar Docker
    docker_ok = shutil.which("docker") is not None
    print(f"    Docker:     {'🟢 Instalado' if docker_ok else '🔴 No encontrado'}")

    # Comprobar servicios
    if docker_ok:
        running = servicios_corriendo()
        print(f"    Servicios:  {'🟢 Corriendo' if running else '🟡 Detenidos'}")

    # Comprobar backend
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=3):
            print(f"    Backend:    🟢 Respondiendo")
    except Exception:
        print(f"    Backend:    🔴 No disponible")

    # Comprobar Grafana
    try:
        with urllib.request.urlopen("http://localhost:3010", timeout=3):
            print(f"    Grafana:    🟢 Respondiendo")
    except Exception:
        print(f"    Grafana:    🔴 No disponible")

    separador()
    print()
    for nombre, url in URLS.items():
        print(f"    {GREEN}→{RESET}  {nombre:25s} {CYAN}{url}{RESET}")
    print()


# ═════════════════════════════════════════════════════════════════════
#  Menú principal
# ═════════════════════════════════════════════════════════════════════

def menu():
    """Muestra el menú interactivo principal."""
    print(f"""
  {WHITE}{BOLD}  ¿Qué quieres hacer?{RESET}

    {GREEN}1{RESET}  🐳  Arranque completo  {DIM}(Docker: Backend + Grafana + MQTT){RESET}
    {CYAN}2{RESET}  🐍  Solo web local      {DIM}(Python directo, sin Docker){RESET}
    {YELLOW}3{RESET}  🎨  Ver diseño del sistema
    {WHITE}4{RESET}  📋  Ver logs en tiempo real
    {WHITE}5{RESET}  📊  Estado del sistema
    {RED}6{RESET}  ⏹️   Detener servicios Docker
    {DIM}0{RESET}  🚪  Salir
""")


def main():
    """Punto de entrada principal."""
    banner()

    while True:
        menu()
        try:
            opcion = input(f"  {WHITE}{BOLD}Elige una opción: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if opcion == "1":
            arrancar_docker()
        elif opcion == "2":
            arrancar_local()
        elif opcion == "3":
            ver_diseno()
        elif opcion == "4":
            ver_logs()
        elif opcion == "5":
            mostrar_estado()
        elif opcion == "6":
            detener_servicios()
        elif opcion == "0":
            break
        else:
            warn("Opción no válida. Elige un número del menú.")

    print(f"\n  {DIM}Hasta luego. 👋{RESET}\n")


if __name__ == "__main__":
    main()
