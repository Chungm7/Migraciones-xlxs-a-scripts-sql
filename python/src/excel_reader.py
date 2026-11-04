"""
Módulo para lectura de Excel, selección de hojas, detección de cabeceras,
limpieza y sanitización de datos de planillas históricas.
"""

import math
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import openpyxl

from config.mappings import CONCEPT_CODE_MAPPING, EVENT_PATTERNS, EXCLUDE_COLUMNS
from src.name_parser import parse_full_name


def list_excel_sheets(excel_path: str) -> List[str]:
    """Retorna los nombres de todas las hojas disponibles en el archivo Excel."""
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    sheets = wb.sheetnames
    wb.close()
    return sheets


def sanitize_amount(val: Any) -> float:
    """
    Sanitiza montos numéricos en double precision.
    Maneja comas decimales, comas de miles (ej. '0,10', '1,800,00', '46,202,00'),
    floats, ints, NaNs y nulos.
    """
    if val is None:
        return 0.0

    if isinstance(val, (int, float)):
        if math.isnan(val):
            return 0.0
        return round(float(val), 2)

    val_str = str(val).strip()
    if not val_str:
        return 0.0

    # Mantener sólo dígitos, puntos, comas y signo negativo
    val_str = re.sub(r"[^\d,\.\-]", "", val_str)
    if not val_str:
        return 0.0

    if "," in val_str and "." in val_str:
        if val_str.rfind(".") > val_str.rfind(","):
            # El punto es decimal, la coma es de miles
            val_str = val_str.replace(",", "")
        else:
            # La coma es decimal, el punto es de miles
            val_str = val_str.replace(".", "").replace(",", ".")
    elif "," in val_str:
        parts = val_str.split(",")
        if len(parts) == 2:
            val_str = parts[0] + "." + parts[1]
        else:
            # Varias comas: todas excepto la última son de miles
            val_str = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return round(float(val_str), 2)
    except ValueError:
        return 0.0


def clean_codigo(val: Any) -> Optional[str]:
    """Limpia el código de trabajador conservando ceros a la izquierda."""
    if val is None:
        return None
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val)).strip()
        return str(val).strip()
    s = str(val).strip()
    return s if s else None


def clean_dni(val: Any) -> Optional[str]:
    """
    Limpia y normaliza el DNI a varchar(8).
    Rellena con ceros a la izquierda si tiene menos de 8 dígitos numéricos.
    """
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val):
            return None
        if val.is_integer():
            val = str(int(val))
        else:
            val = str(val)
    val_str = str(val).strip()
    val_str = re.sub(r"\.0+$", "", val_str)

    digits = re.sub(r"\D", "", val_str)
    if digits:
        return digits.zfill(8)[:8]

    # Si contiene texto no numérico, truncar a 8
    clean = val_str[:8]
    return clean if clean else None


def clean_date(val: Any) -> Optional[str]:
    """
    Convierte una fecha a string 'YYYY-MM-DD' o retorna None si es inválida.
    Soporta objetos datetime/date, formatos texto estándar y números de serie de Excel (ej. '29286.00').
    """
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")

    if isinstance(val, (int, float)):
        if math.isnan(val) or val <= 0:
            return None
        if 1000 <= val <= 60000:
            dt = datetime(1899, 12, 30) + timedelta(days=int(round(val)))
            return dt.strftime("%Y-%m-%d")
        return None

    val_str = str(val).strip()
    if not val_str or val_str.upper() in ("PERMANENTE", "PERMANENTES", "0", "0.0", "0.00", "NULL", "NONE"):
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y", "%d-%m-%y"):
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Soporte para números de serie de Excel almacenados como texto (ej. '29286.00', '35578.00')
    try:
        num = float(val_str.replace(",", "."))
        if 1000 <= num <= 60000:
            dt = datetime(1899, 12, 30) + timedelta(days=int(round(num)))
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return None


def clean_text(val: Any) -> Optional[str]:
    """Retorna un texto limpio o None."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def clean_event_monto(val: Any) -> Optional[str]:
    """Convierte el valor de evento a string limpio ('30', 'SI', 'NO', o None)."""
    if val is None:
        return None
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val)
    s = str(val).strip()
    return s if s else None


def read_payroll_sheet(
    excel_path: str,
    sheet_name: str,
    skip_empty_concepts: bool = False,
) -> Dict[str, Any]:
    """
    Lee una hoja de planilla Excel, localiza cabeceras dinámicamente,
    descarta filas duplicadas vacías y extrae personas, eventos y conceptos.
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)

    # Resolver nombre de hoja si se pasa como número/índice (ej. '1' o 1 para la primera hoja)
    resolved_sheet = None
    if isinstance(sheet_name, int) or (isinstance(sheet_name, str) and str(sheet_name).strip().isdigit()):
        idx = int(sheet_name)
        if 1 <= idx <= len(wb.sheetnames):
            resolved_sheet = wb.sheetnames[idx - 1]
        elif 0 <= idx < len(wb.sheetnames):
            resolved_sheet = wb.sheetnames[idx]

    if not resolved_sheet:
        if sheet_name in wb.sheetnames:
            resolved_sheet = sheet_name
        else:
            for s in wb.sheetnames:
                if s.upper() == str(sheet_name).strip().upper():
                    resolved_sheet = s
                    break

    if not resolved_sheet or resolved_sheet not in wb.sheetnames:
        wb.close()
        raise ValueError(f"La hoja '{sheet_name}' no existe en {excel_path}. Hojas disponibles: {wb.sheetnames}")

    sheet_name = resolved_sheet
    sheet = wb[sheet_name]
    rows = list(sheet.iter_rows(values_only=True))
    wb.close()

    if not rows:
        raise ValueError(f"La hoja '{sheet_name}' está vacía.")

    # 1. Encontrar la fila de cabecera que contiene 'Codigo Trabajador'
    header_idx = None
    for idx, r in enumerate(rows[:25]):
        if r and any(isinstance(c, str) and "Codigo Trabajador" in c for c in r if c is not None):
            header_idx = idx
            break

    if header_idx is None:
        raise ValueError(f"No se encontró la cabecera 'Codigo Trabajador' en las primeras 25 filas de '{sheet_name}'.")

    header = rows[header_idx]
    data_rows = rows[header_idx + 1:]

    # 2. Mapear columnas de eventos
    mapped_events: List[Tuple[int, int, str]] = []  # (col_idx, evhi_id, col_name)
    for col_idx, col_name in enumerate(header):
        if not col_name or not isinstance(col_name, str):
            continue
        c_upper = col_name.strip().upper()
        for pat, evhi_id in EVENT_PATTERNS:
            if pat in c_upper:
                mapped_events.append((col_idx, evhi_id, col_name.strip()))
                break

    # 3. Mapear columnas de conceptos (excluyendo TOTALES y NETO)
    mapped_concepts: List[Tuple[int, int, str]] = []  # (col_idx, cohi_id, col_name)
    for col_idx, col_name in enumerate(header):
        if not col_name or not isinstance(col_name, str):
            continue
        c_str = col_name.strip()
        c_upper = c_str.upper()
        if any(ex in c_upper for ex in EXCLUDE_COLUMNS):
            continue

        # Intentar extraer los primeros 2 dígitos
        m = re.match(r"^(\d{2})", c_str)
        if m:
            code = m.group(1)
            if code in CONCEPT_CODE_MAPPING:
                mapped_concepts.append((col_idx, CONCEPT_CODE_MAPPING[code], c_str))
        else:
            for pat in ("ESSA", "SNP", "SCTR", "IES"):
                if c_upper.startswith(pat):
                    mapped_concepts.append((col_idx, CONCEPT_CODE_MAPPING[pat], c_str))
                    break

    # 4. Filtrar filas de datos válidas (descartando totales o filas vacías)
    raw_valid_rows = []
    for r in data_rows:
        if not r or len(r) < 2:
            continue
        cod_raw = r[0]
        nom_raw = r[1]
        if cod_raw is None or nom_raw is None:
            continue
        cod_str = str(cod_raw).strip()
        nom_str = str(nom_raw).strip()
        if not cod_str or not nom_str:
            continue
        if "TOTAL" in cod_str.upper() or "TOTAL" in nom_str.upper() or "SUBTOTAL" in nom_str.upper():
            continue
        raw_valid_rows.append(r)

    # 5. Agrupar por trabajador para seleccionar la fila rica en datos
    # En caso de duplicados (ej. jornal vs vacaciones vacías), conservar la fila con datos reales
    by_code = defaultdict(list)
    for r in raw_valid_rows:
        code_clean = clean_codigo(r[0])
        if code_clean:
            by_code[code_clean].append(r)

    def score_row(row: Tuple[Any, ...]) -> Tuple[int, int, float]:
        """Calcula el puntaje de datos de una fila: conceptos activos, eventos activos y suma de montos."""
        active_concepts = 0
        total_concept_amt = 0.0
        for col_idx, _, _ in mapped_concepts:
            if col_idx < len(row):
                amt = sanitize_amount(row[col_idx])
                if amt > 0.0:
                    active_concepts += 1
                    total_concept_amt += amt

        active_events = 0
        for col_idx, _, _ in mapped_events:
            if col_idx < len(row):
                val = row[col_idx]
                if val is not None and str(val).strip() not in ("", "0", "0.0"):
                    active_events += 1

        return (active_concepts, active_events, total_concept_amt)

    selected_worker_rows: List[Tuple[Any, ...]] = []
    for code, row_list in by_code.items():
        if len(row_list) == 1:
            best_row = row_list[0]
        else:
            best_row = max(row_list, key=score_row)

        # Validar si la fila contiene datos reales ("si no lo tiene no se pasa")
        sc = score_row(best_row)
        if sc[0] > 0 or sc[1] > 0:
            selected_worker_rows.append(best_row)

    # 6. Construir estructuras estructuradas para generador SQL
    personas: List[Dict[str, Any]] = []
    eventos_persona: List[Dict[str, Any]] = []
    conceptos_persona: List[Dict[str, Any]] = []

    for r in selected_worker_rows:
        pers_codigo = clean_codigo(r[0])
        full_name = clean_text(r[1])
        pers_apelpat, pers_apelmat, pers_nombre = parse_full_name(full_name)

        # Fiel a la estructura del formato de Excel Hoja 1 (DATOS DE IDENTIFICACIÓN):
        # Col 0: Codigo Trabajador
        # Col 1: Apellidos Nombres
        # Col 2: Cargo
        # Col 3: Condición
        # Col 4: Fecha Nacimiento
        # Col 5: Fecha Ingreso
        # Col 6: Fecha Afiliación AFP (pers_afp -> Fecha_AFP)
        # Col 7: DNI / LE (pers_dni)
        # Col 8: C.ESSAL. (pers_c_essal -> C_ESSAL)
        # Col 9: Nombre AFP (pers_nom_afp)
        pers_cargo = clean_text(r[2]) if len(r) > 2 else None
        pers_condicion = clean_text(r[3]) if len(r) > 3 else None
        pers_fechnac = clean_date(r[4]) if len(r) > 4 else None
        pers_ingreso = clean_date(r[5]) if len(r) > 5 else None
        pers_afp = clean_date(r[6]) if len(r) > 6 else None
        pers_dni = clean_dni(r[7]) if len(r) > 7 else None
        pers_c_essal = clean_text(r[8]) if len(r) > 8 else None
        pers_nom_afp = clean_text(r[9]) if len(r) > 9 else None

        # Si el trabajador tiene filas duplicadas en Hoja 1 y algún campo quedó vacío en best_row,
        # consolidar el valor no nulo de sus otras filas para no perder datos de AFP o EsSalud:
        if pers_codigo and len(by_code[pers_codigo]) > 1:
            for other_r in by_code[pers_codigo]:
                if pers_afp is None and len(other_r) > 6:
                    pers_afp = clean_date(other_r[6])
                if pers_c_essal is None and len(other_r) > 8:
                    pers_c_essal = clean_text(other_r[8])
                if pers_nom_afp is None and len(other_r) > 9:
                    pers_nom_afp = clean_text(other_r[9])
                if pers_dni is None and len(other_r) > 7:
                    pers_dni = clean_dni(other_r[7])
                if pers_fechnac is None and len(other_r) > 4:
                    pers_fechnac = clean_date(other_r[4])
                if pers_ingreso is None and len(other_r) > 5:
                    pers_ingreso = clean_date(other_r[5])
                if pers_cargo is None and len(other_r) > 2:
                    pers_cargo = clean_text(other_r[2])
                if pers_condicion is None and len(other_r) > 3:
                    pers_condicion = clean_text(other_r[3])

        persona_record = {
            "pers_codigo": pers_codigo,
            "pers_dni": pers_dni,
            "pers_nombre": pers_nombre,
            "pers_apelpat": pers_apelpat,
            "pers_apelmat": pers_apelmat,
            "pers_fechnac": pers_fechnac,
            "pers_ingreso": pers_ingreso,
            "pers_cargo": pers_cargo,
            "pers_condicion": pers_condicion,
            "pers_afp": pers_afp,
            "pers_nom_afp": pers_nom_afp,
            "pers_c_essal": pers_c_essal,
            "pers_estado": "A",
        }
        personas.append(persona_record)

        # Eventos para este trabajador
        for col_idx, evhi_id, _ in mapped_events:
            val = r[col_idx] if col_idx < len(r) else None
            monto_str = clean_event_monto(val)
            eventos_persona.append({
                "pers_codigo": pers_codigo,
                "pers_dni": pers_dni,
                "evhi_id": evhi_id,
                "monto": monto_str,
                "estado": "A",
            })

        # Conceptos para este trabajador
        for col_idx, cohi_id, _ in mapped_concepts:
            val = r[col_idx] if col_idx < len(r) else None
            monto_num = sanitize_amount(val)
            if skip_empty_concepts and (monto_num == 0.0 or val is None):
                continue
            conceptos_persona.append({
                "pers_codigo": pers_codigo,
                "pers_dni": pers_dni,
                "cohi_id": cohi_id,
                "monto": monto_num,
                "estado": "A",
            })

    return {
        "sheet_name": sheet_name,
        "total_raw_valid_rows": len(raw_valid_rows),
        "total_selected_workers": len(personas),
        "mapped_events_count": len(mapped_events),
        "mapped_concepts_count": len(mapped_concepts),
        "personas": personas,
        "eventos": eventos_persona,
        "conceptos": conceptos_persona,
    }
