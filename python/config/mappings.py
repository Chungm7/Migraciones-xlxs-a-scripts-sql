"""
Catálogos y mapeos para eventos y conceptos históricos de planilla.
Basado en estructura_database.sql e Inserts_Data.sql.
"""

# Catálogo completo de 7 eventos históricos
EVENTOS_CATALOGO = [
    {"evhi_id": 1, "evhi_nom": "D. TRABJ.",        "evhi_tipo": 1, "evhi_estado": "A"},
    {"evhi_id": 2, "evhi_nom": "DOMINIC.",         "evhi_tipo": 1, "evhi_estado": "A"},
    {"evhi_id": 3, "evhi_nom": "VACACIONES",       "evhi_tipo": 2, "evhi_estado": "A"},
    {"evhi_id": 4, "evhi_nom": "SUS / SAN",        "evhi_tipo": 2, "evhi_estado": "A"},
    {"evhi_id": 5, "evhi_nom": "LIC. SIN.",        "evhi_tipo": 2, "evhi_estado": "A"},
    {"evhi_id": 6, "evhi_nom": "LIC.S/GO.",       "evhi_tipo": 2, "evhi_estado": "A"},
    {"evhi_id": 7, "evhi_nom": "SUBSID.E INFERM.", "evhi_tipo": 2, "evhi_estado": "A"},
]

# Reglas de detección para columnas de eventos en el Excel (índice o nombre)
EVENT_PATTERNS = [
    ("D. TRABJ", 1),
    ("DOMINIC", 2),
    ("VACACIONES", 3),
    ("SUS / SAN", 4),
    ("LIC. SIND", 5),
    ("LIC. SIN", 5),
    ("LIC.S/GO", 6),
    ("SUBSID", 7),
]

# Catálogo completo de 45 conceptos históricos
CONCEPTOS_CATALOGO = [
    # Ganancias originales (1 al 17)
    {"cohi_id": 1,  "cohi_tipo": "G", "cohi_cod": "01",  "cohi_nom": "BASICO",     "cohi_estado": "A"},
    {"cohi_id": 2,  "cohi_tipo": "G", "cohi_cod": "02",  "cohi_nom": "R. PERS",    "cohi_estado": "A"},
    {"cohi_id": 3,  "cohi_tipo": "G", "cohi_cod": "04",  "cohi_nom": "B. FAMI",    "cohi_estado": "A"},
    {"cohi_id": 4,  "cohi_tipo": "G", "cohi_cod": "07",  "cohi_nom": "DOMI",       "cohi_estado": "A"},
    {"cohi_id": 5,  "cohi_tipo": "G", "cohi_cod": "09",  "cohi_nom": "7.5% R.",    "cohi_estado": "A"},
    {"cohi_id": 6,  "cohi_tipo": "G", "cohi_cod": "13",  "cohi_nom": "R.M. 149",   "cohi_estado": "A"},
    {"cohi_id": 7,  "cohi_tipo": "G", "cohi_cod": "16",  "cohi_nom": "REINT.",     "cohi_estado": "A"},
    {"cohi_id": 8,  "cohi_tipo": "G", "cohi_cod": "21",  "cohi_nom": "GRAT. V.",   "cohi_estado": "A"},
    {"cohi_id": 9,  "cohi_tipo": "G", "cohi_cod": "25",  "cohi_nom": "FERIAD",     "cohi_estado": "A"},
    {"cohi_id": 10, "cohi_tipo": "G", "cohi_cod": "35",  "cohi_nom": "REF. MO",    "cohi_estado": "A"},
    {"cohi_id": 11, "cohi_tipo": "G", "cohi_cod": "37",  "cohi_nom": "15% DE",     "cohi_estado": "A"},
    {"cohi_id": 12, "cohi_tipo": "G", "cohi_cod": "42",  "cohi_nom": "FUN. MU",    "cohi_estado": "A"},
    {"cohi_id": 13, "cohi_tipo": "G", "cohi_cod": "45",  "cohi_nom": "15% R.V.",   "cohi_estado": "A"},
    {"cohi_id": 14, "cohi_tipo": "G", "cohi_cod": "49",  "cohi_nom": "REDOND",     "cohi_estado": "A"},
    {"cohi_id": 15, "cohi_tipo": "G", "cohi_cod": "50",  "cohi_nom": "INCREM",     "cohi_estado": "A"},
    {"cohi_id": 16, "cohi_tipo": "G", "cohi_cod": "28",  "cohi_nom": "I.C.V.",     "cohi_estado": "A"},
    {"cohi_id": 17, "cohi_tipo": "G", "cohi_cod": "29",  "cohi_nom": "R. FAM.",    "cohi_estado": "A"},

    # Descuentos originales (18 al 34)
    {"cohi_id": 18, "cohi_tipo": "D", "cohi_cod": "53",  "cohi_nom": "S.N.P.",     "cohi_estado": "A"},
    {"cohi_id": 19, "cohi_tipo": "D", "cohi_cod": "56",  "cohi_nom": "ADELAN",     "cohi_estado": "A"},
    {"cohi_id": 20, "cohi_tipo": "D", "cohi_cod": "57",  "cohi_nom": "RETJU",      "cohi_estado": "A"},
    {"cohi_id": 21, "cohi_tipo": "D", "cohi_cod": "59",  "cohi_nom": "MULTAS",     "cohi_estado": "A"},
    {"cohi_id": 22, "cohi_tipo": "D", "cohi_cod": "60",  "cohi_nom": "CAFAE",      "cohi_estado": "A"},
    {"cohi_id": 23, "cohi_tipo": "D", "cohi_cod": "88",  "cohi_nom": "+ VIDA",     "cohi_estado": "A"},
    {"cohi_id": 24, "cohi_tipo": "D", "cohi_cod": "90",  "cohi_nom": "SIND. O",    "cohi_estado": "A"},
    {"cohi_id": 25, "cohi_tipo": "D", "cohi_cod": "58",  "cohi_nom": "AD. SNP",    "cohi_estado": "A"},
    {"cohi_id": 26, "cohi_tipo": "D", "cohi_cod": "80",  "cohi_nom": "IMP. RE.",   "cohi_estado": "A"},
    {"cohi_id": 27, "cohi_tipo": "D", "cohi_cod": "81",  "cohi_nom": "IFP. RE.",   "cohi_estado": "A"},
    {"cohi_id": 28, "cohi_tipo": "D", "cohi_cod": "64",  "cohi_nom": "APORTE",     "cohi_estado": "A"},
    {"cohi_id": 29, "cohi_tipo": "D", "cohi_cod": "72",  "cohi_nom": "SEGURO",     "cohi_estado": "A"},
    {"cohi_id": 30, "cohi_tipo": "D", "cohi_cod": "76",  "cohi_nom": "COM. MI",    "cohi_estado": "A"},
    {"cohi_id": 31, "cohi_tipo": "D", "cohi_cod": "82",  "cohi_nom": "C.V.R.",     "cohi_estado": "A"},
    {"cohi_id": 32, "cohi_tipo": "D", "cohi_cod": "84",  "cohi_nom": "C.A.M.",     "cohi_estado": "A"},
    {"cohi_id": 33, "cohi_tipo": "D", "cohi_cod": "95",  "cohi_nom": "DES. IN",    "cohi_estado": "A"},
    {"cohi_id": 34, "cohi_tipo": "D", "cohi_cod": "99",  "cohi_nom": "DESC. F",    "cohi_estado": "A"},

    # Contribuciones Patronales / Aportes originales (35 al 38)
    {"cohi_id": 35, "cohi_tipo": "A", "cohi_cod": None,  "cohi_nom": "ESSA",       "cohi_estado": "A"},
    {"cohi_id": 36, "cohi_tipo": "A", "cohi_cod": None,  "cohi_nom": "SNP",        "cohi_estado": "A"},
    {"cohi_id": 37, "cohi_tipo": "A", "cohi_cod": None,  "cohi_nom": "SCTR",       "cohi_estado": "A"},
    {"cohi_id": 38, "cohi_tipo": "A", "cohi_cod": None,  "cohi_nom": "IES",        "cohi_estado": "A"},

    # Ganancias faltantes (39 al 42)
    {"cohi_id": 39, "cohi_tipo": "G", "cohi_cod": "14",  "cohi_nom": "BON. EX",    "cohi_estado": "A"},
    {"cohi_id": 40, "cohi_tipo": "G", "cohi_cod": "20",  "cohi_nom": "REIN.V",     "cohi_estado": "A"},
    {"cohi_id": 41, "cohi_tipo": "G", "cohi_cod": "46",  "cohi_nom": "RE. BON",    "cohi_estado": "A"},
    {"cohi_id": 42, "cohi_tipo": "G", "cohi_cod": "47",  "cohi_nom": "REI. BO",    "cohi_estado": "A"},

    # Descuentos faltantes (43 al 45)
    {"cohi_id": 43, "cohi_tipo": "D", "cohi_cod": "65",  "cohi_nom": "ANT. XR",    "cohi_estado": "A"},
    {"cohi_id": 44, "cohi_tipo": "D", "cohi_cod": "67",  "cohi_nom": "DSCT. M",    "cohi_estado": "A"},
    {"cohi_id": 45, "cohi_tipo": "D", "cohi_cod": "68",  "cohi_nom": "SEGUR.",     "cohi_estado": "A"},
]

# Diccionario de búsqueda rápida por código de 2 dígitos o nombre de aportes
CONCEPT_CODE_MAPPING = {
    # Ganancias
    "01": 1,
    "02": 2,
    "04": 3,
    "07": 4,
    "09": 5,
    "13": 6,
    "16": 7,
    "21": 8,
    "25": 9,
    "35": 10,
    "37": 11,
    "42": 12,
    "45": 13,
    "49": 14,
    "50": 15,
    "28": 16,
    "29": 17,
    "14": 39,
    "20": 40,
    "46": 41,
    "47": 42,

    # Descuentos
    "53": 18,
    "56": 19,
    "57": 20,
    "59": 21,
    "60": 22,
    "88": 23,
    "90": 24,
    "58": 25,
    "80": 26,
    "81": 27,
    "64": 28,
    "72": 29,
    "76": 30,
    "82": 31,
    "84": 32,
    "95": 33,
    "99": 34,
    "65": 43,
    "67": 44,
    "68": 45,

    # Contribuciones Patronales
    "ESSA": 35,
    "SNP": 36,
    "SCTR": 37,
    "IES": 38,
}

# Columnas estrictamente excluidas de conceptos
EXCLUDE_COLUMNS = [
    "TOTAL GANANCIAS",
    "TOTAL DESCUENTOS",
    "NETO A PAGAR",
]
