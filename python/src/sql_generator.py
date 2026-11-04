"""
Generador de scripts SQL por lotes e idempotentes para PostgreSQL.
Crea la estructura dividida en 4 secciones, envueltas en transacciones por lotes.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.mappings import CONCEPTOS_CATALOGO, EVENTOS_CATALOGO


def sql_escape_str(val: Optional[str]) -> str:
    """Escapa cadenas de texto para literales SQL en PostgreSQL."""
    if val is None:
        return "NULL"
    escaped = str(val).replace("'", "''")
    return f"'{escaped}'"


def sql_escape_date(val: Optional[str]) -> str:
    """Formatea una fecha con casting explícito o retorna NULL::date para evitar errores 42804 en PostgreSQL."""
    if val is None:
        return "NULL::date"
    return f"'{val}'::date"


def sql_escape_num(val: Optional[float]) -> str:
    """Formatea un número double precision con dos decimales."""
    if val is None:
        return "0.0"
    return f"{float(val):.2f}"


def chunk_list(items: List[Any], chunk_size: int):
    """Generador que divide una lista en bloques de tamaño chunk_size."""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def generate_migration_sql(
    extracted_data: Dict[str, Any],
    periodo: int,
    mes: int,
    schema: str = "public",
    batch_size: int = 500,
    output_dir: str = "output_sql",
) -> str:
    """
    Genera el script SQL por lotes para importar la planilla histórica.
    Retorna la ruta absoluta del archivo .sql generado.
    """
    sheet_name = extracted_data["sheet_name"]
    personas = extracted_data["personas"]
    eventos = extracted_data["eventos"]
    conceptos = extracted_data["conceptos"]

    os.makedirs(output_dir, exist_ok=True)
    sql_filename = f"insert_{sheet_name}_{periodo}_{mes}.sql"
    output_path = os.path.join(output_dir, sql_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        # Encabezado del script
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("-- " + "=" * 78 + "\n")
        f.write(f"-- SCRIPT ETL DE MIGRACION DE PLANILLA HISTORICA A POSTGRESQL\n")
        f.write(f"-- Fecha de Generacion : {now_str}\n")
        f.write(f"-- Hoja Origen         : {sheet_name}\n")
        f.write(f"-- Periodo / Mes       : {periodo} / {mes}\n")
        f.write(f"-- Esquema Destino     : {schema}\n")
        f.write(f"-- Batch Size          : {batch_size}\n")
        f.write(f"-- Total Personas      : {len(personas)}\n")
        f.write(f"-- Total Eventos       : {len(eventos)}\n")
        f.write(f"-- Total Conceptos     : {len(conceptos)}\n")
        f.write("-- " + "=" * 78 + "\n\n")

        f.write("SET client_encoding = 'UTF8';\n")
        f.write("SET standard_conforming_strings = on;\n\n")

        # ====================================================================
        # SECCION 0: ASEGURAR ESQUEMA Y ESTRUCTURA DE TABLAS (DDL IDEMPOTENTE)
        # ====================================================================
        f.write("-- " + "=" * 78 + "\n")
        f.write(f"-- SECCION 0: CREACION IDEMPOTENTE DE ESQUEMA Y TABLAS EN '{schema}'\n")
        f.write("-- " + "=" * 78 + "\n\n")
        f.write("BEGIN;\n\n")
        f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n\n")

        f.write(f"CREATE TABLE IF NOT EXISTS {schema}.tb_concepto_historico (\n")
        f.write("    cohi_id       bigserial PRIMARY KEY,\n")
        f.write("    cohi_tipo     varchar,\n")
        f.write("    cohi_cod      varchar,\n")
        f.write("    cohi_nom      varchar,\n")
        f.write("    cohi_estado   varchar,\n")
        f.write("    usu_info      jsonb,\n")
        f.write("    fecha_created timestamp with time zone DEFAULT now()\n")
        f.write(");\n\n")

        f.write(f"CREATE TABLE IF NOT EXISTS {schema}.tb_persona_historica (\n")
        f.write("    pers_id        bigserial PRIMARY KEY,\n")
        f.write("    pers_nombre    text,\n")
        f.write("    pers_apelpat   text,\n")
        f.write("    pers_apelmat   text,\n")
        f.write("    pers_fechnac   date,\n")
        f.write("    pers_ingreso   date,\n")
        f.write("    pers_cargo     text,\n")
        f.write("    pers_condicion varchar,\n")
        f.write("    pers_afp       date,\n")
        f.write("    pers_nom_afp   varchar,\n")
        f.write("    pers_c_essal   varchar,\n")
        f.write("    pers_dni       varchar(8),\n")
        f.write("    pers_codigo    varchar,\n")
        f.write("    pers_estado    varchar(1) DEFAULT 'A',\n")
        f.write("    usu_info       jsonb,\n")
        f.write("    fecha_created  timestamp with time zone DEFAULT now()\n")
        f.write(");\n\n")

        f.write(f"COMMENT ON COLUMN {schema}.tb_persona_historica.pers_afp IS 'Fecha de Afiliacion AFP (Columna 6 Hoja 1 / Alias export: Fecha_AFP)';\n")
        f.write(f"COMMENT ON COLUMN {schema}.tb_persona_historica.pers_nom_afp IS 'Nombre de la AFP (Columna 9 Hoja 1 / Alias export: pers_nom_afp)';\n")
        f.write(f"COMMENT ON COLUMN {schema}.tb_persona_historica.pers_c_essal IS 'Codigo Autogenerado EsSalud (Columna 8 Hoja 1 / Alias export: C_ESSAL)';\n\n")

        f.write(f"CREATE TABLE IF NOT EXISTS {schema}.tb_concepto_historico_persona (\n")
        f.write("    pers_cohi_id  bigserial PRIMARY KEY,\n")
        f.write("    periodo       integer,\n")
        f.write("    mes           integer,\n")
        f.write(f"    pers_id       integer REFERENCES {schema}.tb_persona_historica (pers_id),\n")
        f.write(f"    cohi_id       integer REFERENCES {schema}.tb_concepto_historico (cohi_id),\n")
        f.write("    monto         double precision,\n")
        f.write("    estado        varchar DEFAULT 'A',\n")
        f.write("    usu_info      jsonb,\n")
        f.write("    fecha_created timestamp with time zone DEFAULT now()\n")
        f.write(");\n\n")

        f.write(f"CREATE TABLE IF NOT EXISTS {schema}.tb_evento_historico (\n")
        f.write("    evhi_id       bigserial PRIMARY KEY,\n")
        f.write("    evhi_nom      text,\n")
        f.write("    evhi_tipo     integer,\n")
        f.write("    evhi_estado   varchar,\n")
        f.write("    usu_info      jsonb,\n")
        f.write("    fecha_created timestamp with time zone DEFAULT now()\n")
        f.write(");\n\n")

        f.write(f"CREATE TABLE IF NOT EXISTS {schema}.tb_evento_historico_persona (\n")
        f.write("    pers_evhi_id  bigserial PRIMARY KEY,\n")
        f.write("    periodo       integer,\n")
        f.write("    mes           integer,\n")
        f.write(f"    pers_id       integer REFERENCES {schema}.tb_persona_historica (pers_id),\n")
        f.write(f"    evhi_id       integer REFERENCES {schema}.tb_evento_historico (evhi_id),\n")
        f.write("    monto         varchar,\n")
        f.write("    estado        varchar DEFAULT 'A',\n")
        f.write("    usu_info      jsonb,\n")
        f.write("    fecha_created timestamp with time zone DEFAULT now()\n")
        f.write(");\n\n")

        f.write("COMMIT;\n\n")

        # ====================================================================
        # SECCION 1: CATALOGOS BASE (7 EVENTOS Y 45 CONCEPTOS)
        # ====================================================================
        f.write("-- " + "=" * 78 + "\n")
        f.write("-- SECCION 1: VERIFICACION E INSERCION IDEMPOTENTE DE CATALOGOS\n")
        f.write("-- " + "=" * 78 + "\n\n")
        f.write("BEGIN;\n\n")

        # 1.1 Catálogo de Eventos (7 filas)
        f.write(f"-- 1.1 Catalogo: {schema}.tb_evento_historico (7 registros)\n")
        f.write(f"INSERT INTO {schema}.tb_evento_historico (evhi_id, evhi_nom, evhi_tipo, evhi_estado, usu_info)\n")
        f.write("SELECT v.evhi_id, v.evhi_nom, v.evhi_tipo, v.evhi_estado, v.usu_info\n")
        f.write("FROM (VALUES\n")
        event_lines = []
        for ev in EVENTOS_CATALOGO:
            e_id = ev["evhi_id"]
            e_nom = sql_escape_str(ev["evhi_nom"])
            e_tipo = ev["evhi_tipo"]
            e_est = sql_escape_str(ev["evhi_estado"])
            event_lines.append(f"    ({e_id}, {e_nom}, {e_tipo}, {e_est}, NULL::jsonb)")
        f.write(",\n".join(event_lines) + "\n")
        f.write(") AS v(evhi_id, evhi_nom, evhi_tipo, evhi_estado, usu_info)\n")
        f.write(f"WHERE NOT EXISTS (\n")
        f.write(f"    SELECT 1 FROM {schema}.tb_evento_historico e WHERE e.evhi_id = v.evhi_id\n")
        f.write(");\n\n")

        f.write(f"SELECT setval(pg_get_serial_sequence('{schema}.tb_evento_historico', 'evhi_id'), (SELECT COALESCE(MAX(evhi_id), 1) FROM {schema}.tb_evento_historico));\n\n")

        # 1.2 Catálogo de Conceptos (45 filas)
        f.write(f"-- 1.2 Catalogo: {schema}.tb_concepto_historico (45 registros)\n")
        f.write(f"INSERT INTO {schema}.tb_concepto_historico (cohi_id, cohi_tipo, cohi_cod, cohi_nom, cohi_estado, usu_info)\n")
        f.write("SELECT v.cohi_id, v.cohi_tipo, v.cohi_cod, v.cohi_nom, v.cohi_estado, v.usu_info\n")
        f.write("FROM (VALUES\n")
        concept_lines = []
        for c in CONCEPTOS_CATALOGO:
            c_id = c["cohi_id"]
            c_tipo = sql_escape_str(c["cohi_tipo"])
            c_cod = sql_escape_str(c["cohi_cod"])
            c_nom = sql_escape_str(c["cohi_nom"])
            c_est = sql_escape_str(c["cohi_estado"])
            concept_lines.append(f"    ({c_id}, {c_tipo}, {c_cod}, {c_nom}, {c_est}, NULL::jsonb)")
        f.write(",\n".join(concept_lines) + "\n")
        f.write(") AS v(cohi_id, cohi_tipo, cohi_cod, cohi_nom, cohi_estado, usu_info)\n")
        f.write(f"WHERE NOT EXISTS (\n")
        f.write(f"    SELECT 1 FROM {schema}.tb_concepto_historico c WHERE c.cohi_id = v.cohi_id\n")
        f.write(");\n\n")

        f.write(f"SELECT setval(pg_get_serial_sequence('{schema}.tb_concepto_historico', 'cohi_id'), (SELECT COALESCE(MAX(cohi_id), 1) FROM {schema}.tb_concepto_historico));\n\n")
        f.write("COMMIT;\n\n")

        # ====================================================================
        # SECCION 2: INSERCION DE PERSONAS HISTORICAS (NO DUPLICAR)
        # ====================================================================
        f.write("-- " + "=" * 78 + "\n")
        f.write(f"-- SECCION 2: INSERCION DE PERSONAS EN {schema}.tb_persona_historica\n")
        f.write("-- (Idempotente: valida con WHERE NOT EXISTS por pers_codigo y pers_dni)\n")
        f.write("-- " + "=" * 78 + "\n\n")

        persona_batches = list(chunk_list(personas, batch_size))
        for b_idx, batch in enumerate(persona_batches, start=1):
            f.write(f"-- Lote Personas {b_idx}/{len(persona_batches)} ({len(batch)} registros)\n")
            f.write("BEGIN;\n")
            f.write(f"INSERT INTO {schema}.tb_persona_historica (\n")
            f.write("    pers_nombre, pers_apelpat, pers_apelmat, pers_fechnac, pers_ingreso,\n")
            f.write("    pers_cargo, pers_condicion, pers_afp, pers_nom_afp, pers_c_essal,\n")
            f.write("    pers_dni, pers_codigo, pers_estado\n")
            f.write(")\n")
            f.write("SELECT\n")
            f.write("    v.pers_nombre, v.pers_apelpat, v.pers_apelmat, v.pers_fechnac::date, v.pers_ingreso::date,\n")
            f.write("    v.pers_cargo, v.pers_condicion, v.pers_afp::date, v.pers_nom_afp, v.pers_c_essal,\n")
            f.write("    v.pers_dni, v.pers_codigo, v.pers_estado\n")
            f.write("FROM (VALUES\n")

            p_lines = []
            for p in batch:
                p_lines.append(
                    f"    ({sql_escape_str(p['pers_nombre'])}, "
                    f"{sql_escape_str(p['pers_apelpat'])}, "
                    f"{sql_escape_str(p['pers_apelmat'])}, "
                    f"{sql_escape_date(p['pers_fechnac'])}, "
                    f"{sql_escape_date(p['pers_ingreso'])}, "
                    f"{sql_escape_str(p['pers_cargo'])}, "
                    f"{sql_escape_str(p['pers_condicion'])}, "
                    f"{sql_escape_date(p['pers_afp'])}, "
                    f"{sql_escape_str(p['pers_nom_afp'])}, "
                    f"{sql_escape_str(p['pers_c_essal'])}, "
                    f"{sql_escape_str(p['pers_dni'])}, "
                    f"{sql_escape_str(p['pers_codigo'])}, "
                    f"{sql_escape_str(p['pers_estado'])})"
                )
            f.write(",\n".join(p_lines) + "\n")
            f.write(") AS v(\n")
            f.write("    pers_nombre, pers_apelpat, pers_apelmat, pers_fechnac, pers_ingreso,\n")
            f.write("    pers_cargo, pers_condicion, pers_afp, pers_nom_afp, pers_c_essal,\n")
            f.write("    pers_dni, pers_codigo, pers_estado\n")
            f.write(")\n")
            f.write(f"WHERE NOT EXISTS (\n")
            f.write(f"    SELECT 1 FROM {schema}.tb_persona_historica p\n")
            f.write(f"    WHERE p.pers_codigo = v.pers_codigo\n")
            f.write(f"       OR (v.pers_dni IS NOT NULL AND p.pers_dni = v.pers_dni)\n")
            f.write(");\n")
            f.write("COMMIT;\n\n")

        # ====================================================================
        # SECCION 3: EVENTOS HISTORICOS POR PERSONA (TIEMPO Y ASISTENCIA)
        # ====================================================================
        f.write("-- " + "=" * 78 + "\n")
        f.write(f"-- SECCION 3: INSERCION DE EVENTOS EN {schema}.tb_evento_historico_persona\n")
        f.write("-- (Resolviendo FK pers_id dinamicamente mediante JOIN por pers_codigo)\n")
        f.write("-- " + "=" * 78 + "\n\n")

        evento_batches = list(chunk_list(eventos, batch_size))
        for b_idx, batch in enumerate(evento_batches, start=1):
            f.write(f"-- Lote Eventos {b_idx}/{len(evento_batches)} ({len(batch)} registros)\n")
            f.write("BEGIN;\n")
            f.write(f"INSERT INTO {schema}.tb_evento_historico_persona (\n")
            f.write("    periodo, mes, pers_id, evhi_id, monto, estado\n")
            f.write(")\n")
            f.write("SELECT\n")
            f.write("    v.periodo, v.mes, p.pers_id, v.evhi_id, v.monto, v.estado\n")
            f.write("FROM (VALUES\n")

            ev_lines = []
            for ev in batch:
                ev_lines.append(
                    f"    ({periodo}, {mes}, {sql_escape_str(ev['pers_codigo'])}, "
                    f"{sql_escape_str(ev['pers_dni'])}, {ev['evhi_id']}, "
                    f"{sql_escape_str(ev['monto'])}, {sql_escape_str(ev['estado'])})"
                )
            f.write(",\n".join(ev_lines) + "\n")
            f.write(") AS v(periodo, mes, pers_codigo, pers_dni, evhi_id, monto, estado)\n")
            f.write(f"JOIN {schema}.tb_persona_historica p\n")
            f.write(f"  ON (p.pers_codigo = v.pers_codigo OR (p.pers_codigo IS NULL AND v.pers_dni IS NOT NULL AND p.pers_dni = v.pers_dni))\n")
            f.write(f"WHERE NOT EXISTS (\n")
            f.write(f"    SELECT 1 FROM {schema}.tb_evento_historico_persona ehp\n")
            f.write(f"    WHERE ehp.periodo = v.periodo\n")
            f.write(f"      AND ehp.mes = v.mes\n")
            f.write(f"      AND ehp.pers_id = p.pers_id\n")
            f.write(f"      AND ehp.evhi_id = v.evhi_id\n")
            f.write(");\n")
            f.write("COMMIT;\n\n")

        # ====================================================================
        # SECCION 4: CONCEPTOS HISTORICOS POR PERSONA (COSTOS Y APORTES)
        # ====================================================================
        f.write("-- " + "=" * 78 + "\n")
        f.write(f"-- SECCION 4: INSERCION DE CONCEPTOS EN {schema}.tb_concepto_historico_persona\n")
        f.write("-- (Resolviendo FK pers_id dinamicamente mediante JOIN por pers_codigo)\n")
        f.write("-- " + "=" * 78 + "\n\n")

        concepto_batches = list(chunk_list(conceptos, batch_size))
        for b_idx, batch in enumerate(concepto_batches, start=1):
            f.write(f"-- Lote Conceptos {b_idx}/{len(concepto_batches)} ({len(batch)} registros)\n")
            f.write("BEGIN;\n")
            f.write(f"INSERT INTO {schema}.tb_concepto_historico_persona (\n")
            f.write("    periodo, mes, pers_id, cohi_id, monto, estado\n")
            f.write(")\n")
            f.write("SELECT\n")
            f.write("    v.periodo, v.mes, p.pers_id, v.cohi_id, v.monto, v.estado\n")
            f.write("FROM (VALUES\n")

            co_lines = []
            for co in batch:
                co_lines.append(
                    f"    ({periodo}, {mes}, {sql_escape_str(co['pers_codigo'])}, "
                    f"{sql_escape_str(co['pers_dni'])}, {co['cohi_id']}, "
                    f"{sql_escape_num(co['monto'])}, {sql_escape_str(co['estado'])})"
                )
            f.write(",\n".join(co_lines) + "\n")
            f.write(") AS v(periodo, mes, pers_codigo, pers_dni, cohi_id, monto, estado)\n")
            f.write(f"JOIN {schema}.tb_persona_historica p\n")
            f.write(f"  ON (p.pers_codigo = v.pers_codigo OR (p.pers_codigo IS NULL AND v.pers_dni IS NOT NULL AND p.pers_dni = v.pers_dni))\n")
            f.write(f"WHERE NOT EXISTS (\n")
            f.write(f"    SELECT 1 FROM {schema}.tb_concepto_historico_persona chp\n")
            f.write(f"    WHERE chp.periodo = v.periodo\n")
            f.write(f"      AND chp.mes = v.mes\n")
            f.write(f"      AND chp.pers_id = p.pers_id\n")
            f.write(f"      AND chp.cohi_id = v.cohi_id\n")
            f.write(");\n")
            f.write("COMMIT;\n\n")

    return output_path
