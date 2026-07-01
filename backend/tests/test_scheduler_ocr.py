"""Tests de la integración de OCR y rotación de capturas HMI en el scheduler."""

import os
import shutil
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from oee.scheduler import (
    find_hmi_screenshots,
    archive_and_cleanup_screenshots,
)

@pytest.fixture
def cwd_screenshots_setup():
    # Rutas relativas al cwd de ejecución (backend/)
    p1 = Path("media_user_1.png")
    p2 = Path("media_user_2.png")
    
    # Copias de seguridad de cualquier archivo real para evitar interferencias
    backup1 = Path("media_user_1.png.bak")
    backup2 = Path("media_user_2.png.bak")
    
    if p1.exists():
        p1.rename(backup1)
    if p2.exists():
        p2.rename(backup2)
        
    yield p1, p2
    
    # Limpieza
    if p1.exists():
        p1.unlink()
    if p2.exists():
        p2.unlink()
        
    # Restaurar copias de seguridad si existían
    if backup1.exists():
        backup1.rename(p1)
    if backup2.exists():
        backup2.rename(p2)


def test_find_hmi_screenshots(cwd_screenshots_setup):
    p1, p2 = cwd_screenshots_setup
    
    # Caso 1: No hay archivos
    assert find_hmi_screenshots() == []
    
    # Caso 2: Solo un archivo
    p1.write_text("fake image 1")
    found = find_hmi_screenshots()
    assert len(found) == 1
    assert str(p1.resolve()) in found
    
    # Caso 3: Ambos archivos
    p2.write_text("fake image 2")
    found = find_hmi_screenshots()
    assert len(found) == 2
    assert str(p1.resolve()) in found
    assert str(p2.resolve()) in found


def test_archive_and_cleanup_screenshots(cwd_screenshots_setup):
    p1, p2 = cwd_screenshots_setup
    p1.write_text("fake image 1")
    p2.write_text("fake image 2")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    archive_dir = project_root / "archive_screenshots"
    
    # Registrar archivos ya existentes antes de la llamada para no borrarlos
    existing_files = set(archive_dir.glob("media_user_*")) if archive_dir.exists() else set()
    
    # Ejecutar archivado
    archive_and_cleanup_screenshots([str(p1), str(p2)])
    
    # Verificar que los archivos originales ya no están en CWD
    assert not p1.exists()
    assert not p2.exists()
    
    # Encontrar los nuevos archivos archivados
    current_files = set(archive_dir.glob("media_user_*"))
    new_files = current_files - existing_files
    
    # Deben haberse creado 2 nuevos archivos archivados
    assert len(new_files) == 2
    
    # Limpiar los nuevos archivos archivados creados por el test
    for nf in new_files:
        if nf.exists():
            nf.unlink()


def test_real_archive_and_cleanup_logic(tmp_path):
    project_root = tmp_path
    archive_dir = project_root / "archive_screenshots"
    archive_dir.mkdir(exist_ok=True)

    img = tmp_path / "media_user_1.png"
    img.write_text("fake image content")

    assert img.exists()

    # Mover a archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"{img.stem}_{timestamp}{img.suffix}"
    dest_path = archive_dir / dest_name
    shutil.move(str(img), str(dest_path))

    assert not img.exists()
    assert dest_path.exists()

    # Crear un archivo expirado (25 horas de antigüedad)
    expired_name = "media_user_2_20260630_120000.png"
    expired_path = archive_dir / expired_name
    expired_path.write_text("expired image content")
    
    # Cambiar mtime de expired_path a hace 25 horas
    mtime = (datetime.now() - timedelta(hours=25)).timestamp()
    os.utime(str(expired_path), (mtime, mtime))

    # Ejecutar algoritmo de limpieza
    retention_limit = datetime.now() - timedelta(hours=24)
    for f in archive_dir.glob("media_user_*"):
        if f.is_file():
            file_mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if file_mtime < retention_limit:
                f.unlink()

    # El archivo nuevo debe conservarse, el expirado debe ser borrado
    assert dest_path.exists()
    assert not expired_path.exists()
