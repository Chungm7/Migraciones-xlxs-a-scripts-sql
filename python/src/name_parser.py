"""
Módulo para la desconcatenación inteligente de Apellidos y Nombres peruanos.
Soporta partículas compuestas (DE, DEL, DE LA, DE LOS, SANTA, SAN, VDA, VDA.DE, etc.).
"""

import re
from typing import Tuple, Optional


def parse_full_name(full_name: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Desconcatena una cadena completa en formato 'APELLIDOS NOMBRES' a:
    (pers_apelpat, pers_apelmat, pers_nombre).

    Reglas:
    - Partículas de Apellido Paterno: 'DE LA', 'DE LOS', 'DE LAS', 'SANTA', 'SAN', 'DEL', 'DE', etc.
    - Partículas de Apellido Materno:
        * Prefijos: 'DE LA', 'DE LOS', 'DE LAS', 'SANTA', 'SAN', 'DEL', 'DE'.
        * Conyugales / Viudez: 'VDA.DE', 'VDA. DE', 'VDA', 'DE' (ej. 'SERQUEN VDA.DE SIPION', 'DIAZ DE VASQUEZ').
    - Si la cadena tiene 2 palabras: primera es paterno, materno es None, segunda es nombre.
    - Si la cadena tiene 1 palabra: primera es paterno, materno y nombre son None.
    """
    if not full_name:
        return None, None, None

    raw = re.sub(r"\s+", " ", str(full_name).strip())
    tokens = raw.split(" ")
    if not tokens or tokens == [""]:
        return None, None, None

    if len(tokens) == 1:
        return tokens[0], None, None

    if len(tokens) == 2:
        return tokens[0], None, tokens[1]

    upper_tokens = [t.upper() for t in tokens]

    # 1. Extracción de Apellido Paterno
    if len(tokens) >= 4 and upper_tokens[0] == "DE" and upper_tokens[1] in ("LA", "LOS", "LAS"):
        paterno = " ".join(tokens[0:3])
        consumed = 3
    elif len(tokens) >= 3 and upper_tokens[0] in ("DE", "DEL", "SAN", "SANTA", "DI", "DA", "VDA", "VDA.", "VDA.DE"):
        paterno = " ".join(tokens[0:2])
        consumed = 2
    else:
        paterno = tokens[0]
        consumed = 1

    remaining = tokens[consumed:]
    if not remaining:
        return paterno, None, None
    if len(remaining) == 1:
        return paterno, None, remaining[0]

    rem_upper = [t.upper() for t in remaining]

    # 2. Extracción de Apellido Materno
    # Prefijos compuestos de materno (dejando al menos 1 token para nombres)
    if len(remaining) >= 4 and rem_upper[0] == "DE" and rem_upper[1] in ("LA", "LOS", "LAS"):
        materno = " ".join(remaining[0:3])
        mat_consumed = 3
    elif len(remaining) >= 3 and rem_upper[0] in ("DE", "DEL", "SAN", "SANTA", "DI", "DA"):
        materno = " ".join(remaining[0:2])
        mat_consumed = 2
    # Partículas de viudez en materno (ej. 'SERQUEN VDA.DE SIPION', 'SERQUEN VDA. DE SIPION')
    elif len(remaining) >= 3 and rem_upper[1] in ("VDA.DE", "VDA.", "VDA"):
        if rem_upper[1] in ("VDA.", "VDA") and len(remaining) >= 4 and rem_upper[2] == "DE":
            materno = " ".join(remaining[0:4])
            mat_consumed = 4
        else:
            materno = " ".join(remaining[0:3])
            mat_consumed = 3
    # Apellido de casada en materno (ej. 'DIAZ DE VASQUEZ FELICITAS')
    elif len(remaining) >= 4 and rem_upper[1] == "DE":
        if len(remaining) >= 5 and rem_upper[2] in ("LA", "LOS", "LAS"):
            materno = " ".join(remaining[0:4])
            mat_consumed = 4
        else:
            materno = " ".join(remaining[0:3])
            mat_consumed = 3
    else:
        materno = remaining[0]
        mat_consumed = 1

    # 3. Nombres (tokens restantes)
    nombres_tokens = remaining[mat_consumed:]
    nombres = " ".join(nombres_tokens) if nombres_tokens else None

    return paterno, materno, nombres
