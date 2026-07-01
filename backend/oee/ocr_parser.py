"""Analizador de OCR para capturas de pantalla de la interfaz HMI."""

import os
import re
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Inicialización diferida de EasyOCR para optimizar la carga del módulo
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # Inicializa EasyOCR con soporte para español e inglés
        _reader = easyocr.Reader(['es', 'en'], verbose=False)
    return _reader

def clean_and_parse_percentage(text: str) -> Optional[float]:
    """Limpia caracteres como % o € y convierte a flotante (0.0 a 1.0)."""
    # Conservar solo dígitos, puntos y comas
    cleaned = re.sub(r'[^\d.,]', '', text)
    if not cleaned:
        return None
    cleaned = cleaned.replace(',', '.')
    try:
        val = float(cleaned)
        # Heurísticas para errores comunes de lectura digital (p. ej., omitir el punto decimal)
        if val > 1000:
            val = val / 100.0
        elif val > 100:
            val = val / 10.0
        
        return val / 100.0
    except ValueError:
        return None

def clean_and_parse_int(text: str) -> Optional[int]:
    """Limpia una cadena para extraer un número entero."""
    cleaned = re.sub(r'[^\d]', '', text)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None

def parse_time_duration_s(text: str) -> Optional[int]:
    """Convierte una cadena de duración HMI (ej. '5h 38m (703)' o 'Oh O3m') a segundos."""
    # Reemplazar 'O' u 'o' por '0' para corregir errores comunes de OCR
    normalized = text.upper().replace('O', '0')
    match = re.search(r'(\d+)\s*H\s*(\d+)\s*M', normalized)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 3600 + minutes * 60
    return None

def parse_hmi_ocr(ocr_texts: List[str]) -> Dict[str, Any]:
    """
    Analiza una lista de cadenas devueltas por EasyOCR.
    Soporta dos pantallas de la HMI:
    1. OEE y KPIs: ['DiSPONIBILIDAD', '7616%', '6986%', 'RENDIMIENTO', '9189%', 'OEE GLOBAL', 'CALIDAD', '9982%']
    2. TURNO: ['TURNO', 'Turno T1', 'Inicio: 07:00', 'Fin: 15.00', 'Piezas Ok', 'Piezas Nok', '681', ...]
    """
    data = {}
    
    # Convertir a minúsculas para búsquedas insensibles a mayúsculas
    texts_lower = [t.lower() for t in ocr_texts]
    
    # 1. Determinar si es la pantalla de OEE y KPIs
    is_oee_page = any(k in t for t in texts_lower for k in ["oee", "disponibilidad", "rendimiento", "calidad"])
    
    if is_oee_page:
        avail = None
        perf = None
        qual = None
        
        # Regla de proximidad: el valor suele ser el elemento siguiente a la etiqueta
        for i, text in enumerate(texts_lower):
            if "disponibilidad" in text and i + 1 < len(ocr_texts):
                avail = clean_and_parse_percentage(ocr_texts[i + 1])
            elif "rendimiento" in text and i + 1 < len(ocr_texts):
                perf = clean_and_parse_percentage(ocr_texts[i + 1])
            elif "calidad" in text and i + 1 < len(ocr_texts):
                qual = clean_and_parse_percentage(ocr_texts[i + 1])
                
        # Extraer todos los valores de porcentaje viables en la lista
        pct_values = []
        for t in ocr_texts:
            val = clean_and_parse_percentage(t)
            if val is not None and 0.0 <= val <= 1.0:
                if val not in pct_values:
                    pct_values.append(val)
                    
        # Validación matemática: OEE = Disponibilidad * Rendimiento * Calidad
        oee = None
        if len(pct_values) >= 3:
            if avail is not None and perf is not None and qual is not None:
                calculated_oee = avail * perf * qual
                # Buscar el porcentaje leído más cercano al OEE calculado matemáticamente
                closest_val = min(pct_values, key=lambda x: abs(x - calculated_oee))
                if abs(closest_val - calculated_oee) < 0.05:
                    oee = closest_val
                else:
                    oee = calculated_oee
            else:
                # Heurística: el OEE suele ser el menor de los porcentajes no nulos
                sorted_pcts = sorted(pct_values)
                oee = sorted_pcts[0]
                
        # Fallbacks si alguna métrica falló por proximidad
        if not avail and pct_values:
            candidates = [v for v in pct_values if v != oee]
            if len(candidates) >= 1:
                avail = candidates[0]
        if not perf and pct_values:
            candidates = [v for v in pct_values if v != oee and v != avail]
            if len(candidates) >= 1:
                perf = candidates[0]
        if not qual and pct_values:
            candidates = [v for v in pct_values if v != oee and v != avail and v != perf]
            if len(candidates) >= 1:
                qual = candidates[0]
 
        if avail is not None: data["availability"] = avail
        if perf is not None: data["performance"] = perf
        if qual is not None: data["quality"] = qual
        if oee is not None: data["oee"] = oee
 
    # 2. Determinar si es la pantalla del TURNO
    is_turno_page = any(k in t for t in texts_lower for k in ["turno", "piezas", "tiempo en marcha", "tiempo parada"])
    
    if is_turno_page:
        # Extraer el turno (T1, T2, T3)
        shift_label = None
        for text in ocr_texts:
            match = re.search(r'turno\s+(T\d)', text, re.IGNORECASE)
            if match:
                shift_label = match.group(1).upper()
                break
        if not shift_label:
            for text in ocr_texts:
                for sh in ["T1", "T2", "T3"]:
                    if sh in text.upper():
                        shift_label = sh
                        break
                if shift_label:
                    break
        
        if shift_label:
            data["shift_label"] = shift_label

        # Extraer duraciones de tiempo
        run_time_s = None
        stop_time_s = None
        error_time_s = None
        for i, text in enumerate(texts_lower):
            if "tiempo en marcha" in text and i + 1 < len(ocr_texts):
                run_time_s = parse_time_duration_s(ocr_texts[i + 1])
            elif "tiempo parada" in text and i + 1 < len(ocr_texts):
                stop_time_s = parse_time_duration_s(ocr_texts[i + 1])
            elif "tiempo error" in text and i + 1 < len(ocr_texts):
                error_time_s = parse_time_duration_s(ocr_texts[i + 1])

        if run_time_s is not None:
            data["run_time_s"] = run_time_s
            if stop_time_s is not None and error_time_s is not None:
                data["planned_time_s"] = run_time_s + stop_time_s + error_time_s
            
        # Extraer piezas OK y NOK
        good_pieces = None
        bad_pieces = None
        
        ok_idx = -1
        nok_idx = -1
        for i, text in enumerate(texts_lower):
            if "piezas ok" in text or "piezasok" in text:
                ok_idx = i
            elif "piezas nok" in text or "piezasnok" in text or "piezas no ok" in text:
                nok_idx = i
                
        # Buscar todos los enteros limpios y sus índices correspondientes
        candidates = []
        for i, t in enumerate(ocr_texts):
            val = clean_and_parse_int(t)
            if val is not None and not re.search(r'[a-zA-Z]', t):
                candidates.append((i, val))
                
        if ok_idx != -1 or nok_idx != -1:
            # Filtrar candidatos que están después del primer label encontrado
            first_label_idx = min(idx for idx in [ok_idx, nok_idx] if idx != -1)
            valid_candidates = [c for c in candidates if c[0] > first_label_idx]
            
            if len(valid_candidates) == 1:
                # Si solo hay un número después de los labels, es el OK y el NOK es 0
                good_pieces = valid_candidates[0][1]
                bad_pieces = 0
            elif len(valid_candidates) >= 2:
                # Si hay dos o más números
                if ok_idx != -1 and nok_idx != -1 and ok_idx < nok_idx:
                    between = [c for c in valid_candidates if ok_idx < c[0] < nok_idx]
                    after_nok = [c for c in valid_candidates if c[0] > nok_idx]
                    if between and after_nok:
                        good_pieces = between[0][1]
                        bad_pieces = after_nok[0][1]
                    else:
                        good_pieces = valid_candidates[0][1]
                        bad_pieces = valid_candidates[1][1]
                else:
                    good_pieces = valid_candidates[0][1]
                    bad_pieces = valid_candidates[1][1]
                
        if good_pieces is not None:
            data["good_pieces"] = good_pieces
            data["total_pieces"] = good_pieces + (bad_pieces or 0)
            
    return data

def extract_metrics_from_images(image_paths: List[str]) -> Dict[str, Any]:
    """Lee y procesa una lista de imágenes para consolidar las métricas de OEE."""
    merged_data = {}
    reader = get_reader()
    
    for img_path in image_paths:
        if not os.path.exists(img_path):
            logger.warning("Ruta de imagen no encontrada para OCR: %s", img_path)
            continue
            
        try:
            logger.info("Ejecutando EasyOCR en: %s", img_path)
            ocr_texts = reader.readtext(img_path, detail=0)
            logger.info("EasyOCR recuperó: %s", ocr_texts)
            parsed = parse_hmi_ocr(ocr_texts)
            logger.info("Métricas parseadas: %s", parsed)
            merged_data.update(parsed)
        except Exception as exc:
            logger.error("Error al procesar %s en OCR: %s", img_path, exc, exc_info=True)
            
    return merged_data
