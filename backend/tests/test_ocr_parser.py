"""Tests del analizador de OCR para capturas de pantalla de la HMI."""

import os
import pytest
from oee.ocr_parser import (
    clean_and_parse_percentage,
    clean_and_parse_int,
    parse_time_duration_s,
    parse_hmi_ocr,
    extract_metrics_from_images,
)

# ── Tests Unitarios de Funciones de Limpieza y Parseo ─────────────────────────

def test_clean_and_parse_percentage():
    assert clean_and_parse_percentage("7616%") == pytest.approx(0.7616)
    assert clean_and_parse_percentage("99,82%") == pytest.approx(0.9982)
    assert clean_and_parse_percentage("69.86") == pytest.approx(0.6986)
    assert clean_and_parse_percentage("") is None
    assert clean_and_parse_percentage("abc") is None
    # Heurística para errores comunes de lectura digital (p. ej. sin punto decimal)
    assert clean_and_parse_percentage("9189") == pytest.approx(0.9189)
    assert clean_and_parse_percentage("918.9") == pytest.approx(0.9189)


def test_clean_and_parse_int():
    assert clean_and_parse_int("681") == 681
    assert clean_and_parse_int("0") == 0
    assert clean_and_parse_int("abc") is None
    assert clean_and_parse_int("12abc34") == 1234


def test_parse_time_duration_s():
    assert parse_time_duration_s("5h 38m (703)") == 5 * 3600 + 38 * 60
    assert parse_time_duration_s("Oh O3m") == 3 * 60
    assert parse_time_duration_s("2H 15M") == 2 * 3600 + 15 * 60
    assert parse_time_duration_s("invalid") is None


# ── Tests Unitarios del Parser HMI ───────────────────────────────────────────

def test_parse_hmi_ocr_oee_page():
    ocr_texts = [
        "DiSPONIBILIDAD",
        "7616%",
        "6986%",
        "RENDIMIENTO",
        "9189%",
        "OEE GLOBAL",
        "CALIDAD",
        "9982%",
    ]
    parsed = parse_hmi_ocr(ocr_texts)
    assert parsed.get("availability") == pytest.approx(0.7616)
    assert parsed.get("performance") == pytest.approx(0.9189)
    assert parsed.get("quality") == pytest.approx(0.9982)
    assert parsed.get("oee") == pytest.approx(0.6986)


def test_parse_hmi_ocr_turno_page():
    ocr_texts = [
        "TURNO",
        "Turno T1",
        "Inicio: 07:00",
        "Fin: 15.00",
        "Piezas Ok",
        "681",
        "Piezas Nok",
        "0",
        "TIEMPO EN MARCHA",
        "5h 38m",
        "TIEMPO PARADA",
        "2h 22m",
        "TIEMPO ERROR",
        "0h 00m",
    ]
    parsed = parse_hmi_ocr(ocr_texts)
    assert parsed.get("shift_label") == "T1"
    assert parsed.get("good_pieces") == 681
    assert parsed.get("total_pieces") == 681
    assert parsed.get("run_time_s") == 5 * 3600 + 38 * 60
    assert parsed.get("planned_time_s") == (5 * 3600 + 38 * 60) + (2 * 3600 + 22 * 60)


# ── Tests de Integración con Imágenes Reales (Golden Snapshots) ────────────────

@pytest.mark.ocr
def test_extract_metrics_from_golden_images():
    # Rutas de las imágenes de prueba
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img1 = os.path.join(base_dir, "data", "media_user_1.png")
    img2 = os.path.join(base_dir, "data", "media_user_2.png")

    assert os.path.exists(img1), f"Falta el snapshot dorado: {img1}"
    assert os.path.exists(img2), f"Falta el snapshot dorado: {img2}"

    # Ejecutar extracción de métricas
    metrics = extract_metrics_from_images([img1, img2])

    # Verificar que se extrajeron las métricas esperadas del conjunto de imágenes dorado
    assert "oee" in metrics
    assert "availability" in metrics
    assert "performance" in metrics
    assert "quality" in metrics
    assert "shift_label" in metrics
    assert "good_pieces" in metrics
    assert "total_pieces" in metrics
    assert "run_time_s" in metrics
    assert "planned_time_s" in metrics

    # Valores específicos basados en los snapshots actuales
    assert metrics["availability"] == pytest.approx(0.7616)
    assert metrics["performance"] == pytest.approx(0.9189)
    assert metrics["quality"] == pytest.approx(0.9982)
    assert metrics["oee"] == pytest.approx(0.6986)
    assert metrics["shift_label"] == "T1"
    assert metrics["good_pieces"] == 681
    assert metrics["total_pieces"] == 681
