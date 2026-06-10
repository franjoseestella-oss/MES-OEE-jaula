#!/usr/bin/env python3
"""
Lanzador de la aplicación MES/OEE — Logisnext
Uso: python launcher.py  (o doble clic en Windows)
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

# ── Colores ANSI ──────────────────────────────────────────────────────────────
if sys.platform == "win32":
    os.system("color")  # habilitar ANSI en Windows

R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
C  = "\033[96m"
W  = "\033[97m"
DIM = "\033[2m"
RST = "\033[0m"

BANNER = f"""
{C}╔══════════════════════════════════════════════════════╗
║  {W}LOGISNEXT  ·  MES / OEE  ·  Lanzador v1.0{C}           ║
╚══════════════════════════════════════════════════════╝{RST}
"""

ROOT = Path(__file__).parent
ENV_FILE  = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
COMPOSE   = ROOT / "docker-compose.yml"

URLS = {
    "Backend / Chatbot": "http://localhost:8000",
    "Grafana":           "http://localhost:3010/d/mes-home-v1/logisnext-e28094-inicio?orgId=1&refresh=10s",
    "API Docs":          "http://localhost:8000/docs",
}

HEALTH_URL    = "http://localhost:8000/health"
GRAFANA_URL   = "http://localhost:3010"
WAIT_TIMEOUT  = 120   # segundos máximos de espera
POLL_INTERVAL = 3


# ── Utilidades ────────────────────────────────────────────────────────────────

def step(msg: str) -> None:
    print(f"\n{C}▶{RST}  {W}{msg}{RST}")

def ok(msg: str) -> None:
    print(f"   {G}✓{RST}  {msg}")

def warn(msg: str) -> None:
    print(f"   {Y}⚠{RST}  {msg}")

def err(msg: str) -> None:
    print(f"   {R}✗{RST}  {R}{msg}{RST}")

def die(msg: str) -> None:
    err(msg)
    input(f"\n{DIM}Pulsa INTRO para salir…{RST}")
    sys.exit(1)

def wait_for_http(url: str, timeout: int = WAIT_TIMEOUT) -> bool:
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


# ── Comprobaciones previas ────────────────────────────────────────────────────

def check_docker() -> None:
    step("Verificando Docker…")
    if shutil.which("docker") is None:
        die("Docker no está instalado o no está en el PATH.")
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            die("Docker Desktop no está en marcha. Ábrelo y vuelve a intentarlo.")
    except subprocess.TimeoutExpired:
        die("Docker no responde (timeout). Comprueba que está corriendo.")
    ok("Docker disponible y en marcha.")


def check_env() -> None:
    step("Verificando archivo .env…")
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            warn(".env no encontrado — se ha copiado .env.example.")
            warn("Edita .env con tus credenciales antes de continuar.")
            print()
            resp = input(f"   {Y}¿Quieres editar .env ahora? (s/n): {RST}").strip().lower()
            if resp == "s":
                if sys.platform == "win32":
                    os.startfile(str(ENV_FILE))
                else:
                    subprocess.Popen(["xdg-open", str(ENV_FILE)])
                input(f"\n   {DIM}Guarda el archivo y pulsa INTRO para continuar…{RST}")
        else:
            die(".env.example no encontrado. Revisa la integridad del proyecto.")
    else:
        ok(".env encontrado.")


def check_compose() -> None:
    if not COMPOSE.exists():
        die(f"docker-compose.yml no encontrado en {ROOT}")


# ── Control de Docker Compose ─────────────────────────────────────────────────

def compose_cmd(*args) -> list[str]:
    # Compatibilidad con docker compose v2 y docker-compose v1
    if shutil.which("docker-compose"):
        return ["docker-compose"] + list(args)
    return ["docker", "compose"] + list(args)


def services_running() -> bool:
    result = subprocess.run(
        compose_cmd("ps", "--services", "--filter", "status=running"),
        cwd=ROOT, capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def start_services() -> None:
    step("Iniciando servicios con Docker Compose…")
    print(f"   {DIM}(esto puede tardar 1-2 min la primera vez mientras descarga imágenes){RST}\n")
    result = subprocess.run(
        compose_cmd("up", "--build", "-d"),
        cwd=ROOT
    )
    if result.returncode != 0:
        die("docker-compose up falló. Revisa el mensaje de error arriba.")
    ok("Contenedores iniciados.")


def stop_services() -> None:
    step("Deteniendo servicios…")
    subprocess.run(compose_cmd("down"), cwd=ROOT)
    ok("Servicios detenidos.")


# ── Espera y apertura de URLs ─────────────────────────────────────────────────

def wait_and_open() -> None:
    step(f"Esperando que el backend esté listo (máx. {WAIT_TIMEOUT}s)…")
    sys.stdout.write("   ")
    sys.stdout.flush()

    deadline = time.time() + WAIT_TIMEOUT
    backend_ok = False
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=3) as r:
                if r.status < 500:
                    backend_ok = True
                    break
        except Exception:
            pass
        sys.stdout.write(f"{C}·{RST}")
        sys.stdout.flush()
        time.sleep(POLL_INTERVAL)
    print()

    if not backend_ok:
        warn(f"El backend no respondió en {WAIT_TIMEOUT}s. Puede que aún esté arrancando.")
    else:
        ok(f"Backend listo en {HEALTH_URL}")

    # Abrir URLs en el navegador
    step("Abriendo aplicación en el navegador…")
    for nombre, url in URLS.items():
        print(f"   {G}→{RST}  {nombre}: {C}{url}{RST}")
    print()
    time.sleep(1)
    webbrowser.open(URLS["Backend / Chatbot"])
    time.sleep(0.5)
    webbrowser.open(URLS["Grafana"])


# ── Menú principal ────────────────────────────────────────────────────────────

def print_menu() -> None:
    print(f"""
{W}  Opciones:{RST}
    {G}1{RST}  Iniciar aplicación
    {Y}2{RST}  Ver logs en tiempo real
    {R}3{RST}  Detener aplicación
    {C}4{RST}  Mostrar URLs
    {DIM}0{RST}  Salir
""")


def show_urls() -> None:
    print()
    for nombre, url in URLS.items():
        print(f"   {G}→{RST}  {nombre:30s} {C}{url}{RST}")


def stream_logs() -> None:
    step("Mostrando logs (Ctrl+C para salir)…")
    try:
        subprocess.run(compose_cmd("logs", "-f", "--tail=50"), cwd=ROOT)
    except KeyboardInterrupt:
        print(f"\n   {DIM}Logs detenidos.{RST}")


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    print(BANNER)
    check_docker()
    check_env()
    check_compose()

    while True:
        print_menu()
        try:
            choice = input(f"  {W}Elige una opción: {RST}").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "1":
            start_services()
            wait_and_open()
        elif choice == "2":
            if not services_running():
                warn("Los servicios no están corriendo. Inícielos primero (opción 1).")
            else:
                stream_logs()
        elif choice == "3":
            stop_services()
        elif choice == "4":
            show_urls()
        elif choice == "0":
            break
        else:
            warn("Opción no válida.")

    print(f"\n{DIM}  Hasta luego.{RST}\n")


if __name__ == "__main__":
    main()
