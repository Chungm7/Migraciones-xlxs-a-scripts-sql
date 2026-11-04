#!/usr/bin/env python3
"""
CLI interactivo y por argumentos para la generación de scripts SQL por lotes
a partir de planillas históricas en Excel.
"""

import argparse
import glob
import os
import sys
from typing import List, Optional

# Asegurar que el directorio 'python' esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.excel_reader import list_excel_sheets, read_payroll_sheet
from src.sql_generator import generate_migration_sql

MONTH_MAPPING = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SETIEMBRE": 9,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
}


def find_candidate_excel_files() -> List[str]:
    """Busca archivos .xlsx en el directorio actual, en ../ y subdirectorios."""
    search_patterns = [
        os.path.join(BASE_DIR, "*.xlsx"),
        os.path.join(BASE_DIR, "..", "*.xlsx"),
        os.path.join(BASE_DIR, "data", "*.xlsx"),
        os.path.join(BASE_DIR, "..", "data", "*.xlsx"),
    ]
    candidates = []
    for pat in search_patterns:
        for f in glob.glob(pat):
            clean_f = os.path.abspath(f)
            if clean_f not in candidates and not os.path.basename(clean_f).startswith("~$"):
                candidates.append(clean_f)
    return candidates


def interactive_prompt() -> dict:
    """Ejecuta un menú interactivo en terminal para configurar los parámetros del ETL."""
    print("\n" + "=" * 65)
    print("   ETL GENERADOR DE SCRIPTS SQL - PLANILLAS HISTORICAS")
    print("=" * 65)

    # 1. Selección de archivo Excel
    candidates = find_candidate_excel_files()
    excel_path = None
    if candidates:
        print("\nArchivos Excel encontrados:")
        for idx, c in enumerate(candidates, start=1):
            rel = os.path.relpath(c, BASE_DIR)
            print(f"  [{idx}] {rel}")
        print(f"  [{len(candidates) + 1}] Ingresar otra ruta manualmente")

        choice = input(f"\nSeleccione un archivo [1-{len(candidates) + 1}] (Default: 1): ").strip()
        if not choice or choice == "1":
            excel_path = candidates[0]
        elif choice.isdigit() and 1 <= int(choice) <= len(candidates):
            excel_path = candidates[int(choice) - 1]
        else:
            excel_path = input("Ingrese la ruta del archivo Excel: ").strip()
    else:
        excel_path = input("Ingrese la ruta del archivo Excel: ").strip()

    if not os.path.isfile(excel_path):
        print(f"\n[ERROR] El archivo '{excel_path}' no existe.")
        sys.exit(1)

    # 2. Selección de hoja
    available_sheets = list_excel_sheets(excel_path)
    print("\nHojas disponibles en el archivo:")
    for idx, s in enumerate(available_sheets, start=1):
        print(f"  [{idx}] {s}")

    sheet_choice = input(f"\nSeleccione la hoja a procesar [1-{len(available_sheets)}] (Default: 1): ").strip()
    if not sheet_choice:
        sheet_name = available_sheets[0]
    elif sheet_choice.isdigit() and 1 <= int(sheet_choice) <= len(available_sheets):
        sheet_name = available_sheets[int(sheet_choice) - 1]
    else:
        sheet_name = sheet_choice

    # 3. Periodo
    default_periodo = 2015
    periodo_input = input(f"\nPeriodo / Año (Default: {default_periodo}): ").strip()
    periodo = int(periodo_input) if periodo_input.isdigit() else default_periodo

    # 4. Mes (deducir del nombre de la hoja si aplica)
    deduced_mes = MONTH_MAPPING.get(sheet_name.upper().strip(), 1)
    mes_input = input(f"Mes (1-12) (Default: {deduced_mes}): ").strip()
    mes = int(mes_input) if mes_input.isdigit() else deduced_mes

    # 5. Esquema PostgreSQL
    schema_input = input("Esquema destino en PostgreSQL (Default: public): ").strip()
    schema = schema_input if schema_input else "public"

    # 6. Tamaño de lote
    batch_input = input("Tamaño de lote / batch-size (Default: 500): ").strip()
    batch_size = int(batch_input) if batch_input.isdigit() else 500

    # 7. Skip empty concepts
    skip_input = input("¿Omitir inserción de conceptos con monto en 0.0? [s/N] (Default: N): ").strip().lower()
    skip_empty_concepts = skip_input in ("s", "si", "y", "yes", "true")

    return {
        "excel": excel_path,
        "sheet": sheet_name,
        "periodo": periodo,
        "mes": mes,
        "schema": schema,
        "batch_size": batch_size,
        "skip_empty_concepts": skip_empty_concepts,
    }


def parse_arguments() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="ETL generador de scripts SQL por lotes para migración de planillas históricas."
    )
    parser.add_argument(
        "--excel",
        type=str,
        default=None,
        help="Ruta al archivo Excel (.xlsx).",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        default=None,
        help="Nombre de la hoja target (ej. ENERO, FEBRERO).",
    )
    parser.add_argument(
        "--periodo",
        type=int,
        default=None,
        help="Año / periodo (ej. 2015).",
    )
    parser.add_argument(
        "--mes",
        type=int,
        default=None,
        help="Número de mes (1 al 12).",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default="public",
        help="Nombre del esquema en PostgreSQL (default: public).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Cantidad máxima de registros por bloque INSERT (default: 500).",
    )
    parser.add_argument(
        "--skip-empty-concepts",
        action="store_true",
        help="Omitir conceptos cuyo monto sea 0.0 o nulo.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Si no se pasó al menos --excel o --sheet, entrar en modo interactivo
    if args.excel is None or args.sheet is None:
        params = interactive_prompt()
    else:
        excel_path = os.path.abspath(args.excel)
        if not os.path.isfile(excel_path):
            print(f"[ERROR] El archivo '{excel_path}' no existe.")
            sys.exit(1)

        sheet_name = args.sheet
        periodo = args.periodo if args.periodo is not None else 2015
        mes = args.mes if args.mes is not None else MONTH_MAPPING.get(sheet_name.upper().strip(), 1)
        schema = args.schema
        batch_size = args.batch_size
        skip_empty_concepts = args.skip_empty_concepts

        params = {
            "excel": excel_path,
            "sheet": sheet_name,
            "periodo": periodo,
            "mes": mes,
            "schema": schema,
            "batch_size": batch_size,
            "skip_empty_concepts": skip_empty_concepts,
        }

    print("\n" + "-" * 65)
    print("Iniciando procesamiento ETL con la siguiente configuración:")
    print(f"  • Archivo Excel : {params['excel']}")
    print(f"  • Hoja Target   : {params['sheet']}")
    print(f"  • Periodo / Mes : {params['periodo']} / {params['mes']}")
    print(f"  • Esquema BD    : {params['schema']}")
    print(f"  • Batch Size    : {params['batch_size']}")
    print(f"  • Skip 0.0      : {params['skip_empty_concepts']}")
    print("-" * 65)

    print("\n[1/3] Leyendo archivo Excel y analizando cabeceras...")
    extracted_data = read_payroll_sheet(
        excel_path=params["excel"],
        sheet_name=params["sheet"],
        skip_empty_concepts=params["skip_empty_concepts"],
    )

    print(f"      - Filas brutas válidas analizadas : {extracted_data['total_raw_valid_rows']}")
    print(f"      - Trabajadores únicos con data   : {extracted_data['total_selected_workers']}")
    print(f"      - Columnas de eventos detectadas : {extracted_data['mapped_events_count']}")
    print(f"      - Columnas conceptos detectadas  : {extracted_data['mapped_concepts_count']}")

    print("\n[2/3] Generando script SQL idempotente y por lotes...")
    output_dir = os.path.join(BASE_DIR, "output_sql")
    sql_path = generate_migration_sql(
        extracted_data=extracted_data,
        periodo=params["periodo"],
        mes=params["mes"],
        schema=params["schema"],
        batch_size=params["batch_size"],
        output_dir=output_dir,
    )

    file_size_kb = os.path.getsize(sql_path) / 1024
    file_size_mb = file_size_kb / 1024

    print("\n[3/3] ¡Proceso completado exitosamente!")
    print(f"      - Registros personas a insertar : {len(extracted_data['personas'])}")
    print(f"      - Registros eventos a insertar  : {len(extracted_data['eventos'])}")
    print(f"      - Registros conceptos a insertar: {len(extracted_data['conceptos'])}")
    print(f"      - Archivo SQL generado         : {sql_path}")
    print(f"      - Tamaño del archivo SQL       : {file_size_mb:.2f} MB ({file_size_kb:.1f} KB)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
