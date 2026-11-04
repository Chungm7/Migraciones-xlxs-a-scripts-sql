-- ==============================================================================
-- CONSULTAS DE EXPORTACIÓN Y VERIFICACIÓN DE PLANILLA HISTÓRICA
-- Mapeo Fiel al Formato de Hoja 1:
--   • P.pers_afp   AS Fecha_AFP  (Columna 6: Fecha Afiliación AFP)
--   • P.pers_nom_afp              (Columna 9: Nombre AFP)
--   • P.pers_c_essal AS C_ESSAL   (Columna 8: C.ESSAL.)
-- ==============================================================================

-- 1. Consulta Completa de Trabajador (Datos Personales + Eventos + Conceptos)
SELECT
    -- Datos de Identificación Persona (Hoja 1)
    P.pers_codigo     AS Codigo_Trabajador,
    P.pers_apelpat    AS Apellido_Paterno,
    P.pers_apelmat    AS Apellido_Materno,
    P.pers_nombre     AS Nombre,
    P.pers_dni        AS DNI_LE,
    P.pers_cargo      AS Cargo,
    P.pers_condicion  AS Condicion,
    P.pers_fechnac    AS Fecha_Nacimiento,
    P.pers_ingreso    AS Fecha_Ingreso,
    P.pers_afp        AS Fecha_AFP,
    P.pers_nom_afp    AS pers_nom_afp,
    P.pers_c_essal    AS C_ESSAL,

    -- Datos de Tiempo y Asistencia (Evento Histórico)
    EH.evhi_nom       AS Nombre_Evento,
    EHP.periodo       AS Periodo_Evento,
    EHP.mes           AS Mes_Evento,
    EHP.monto         AS Valor_Evento,

    -- Datos Monetarios y Contribuciones (Concepto Histórico)
    CH.cohi_nom       AS Nombre_Concepto,
    CHP.periodo       AS Periodo_Concepto,
    CHP.mes           AS Mes_Concepto,
    CHP.monto         AS Valor_Concepto

FROM tb_persona_historica AS P
    LEFT JOIN tb_evento_historico_persona AS EHP ON EHP.pers_id = P.pers_id
    LEFT JOIN tb_evento_historico AS EH ON EH.evhi_id = EHP.evhi_id
    LEFT JOIN tb_concepto_historico_persona AS CHP ON CHP.pers_id = P.pers_id
    LEFT JOIN tb_concepto_historico AS CH ON CH.cohi_id = CHP.cohi_id
WHERE P.pers_codigo = '0487';


-- 2. Consulta de Conceptos Monetarios por Trabajador y Periodo/Mes
SELECT
    -- Datos de Identificación Persona (Hoja 1)
    P.pers_codigo     AS Codigo_Trabajador,
    P.pers_apelpat    AS Apellido_Paterno,
    P.pers_apelmat    AS Apellido_Materno,
    P.pers_nombre     AS Nombre,
    P.pers_dni        AS DNI_LE,
    P.pers_cargo      AS Cargo,
    P.pers_condicion  AS Condicion,
    P.pers_fechnac    AS Fecha_Nacimiento,
    P.pers_ingreso    AS Fecha_Ingreso,
    P.pers_afp        AS Fecha_AFP,
    P.pers_nom_afp    AS pers_nom_afp,
    P.pers_c_essal    AS C_ESSAL,

    -- Conceptos
    CH.cohi_cod       AS Codigo_Concepto,
    CH.cohi_nom       AS Nombre_Concepto,
    CHP.periodo       AS Periodo,
    CHP.mes           AS Mes,
    CHP.monto         AS Valor_Concepto

FROM tb_persona_historica AS P
    INNER JOIN tb_concepto_historico_persona AS CHP ON CHP.pers_id = P.pers_id
    INNER JOIN tb_concepto_historico AS CH ON CH.cohi_id = CHP.cohi_id
WHERE CHP.periodo = 2026 AND CHP.mes = 2;


-- 3. Consulta de Eventos (Asistencia / Licencias / Subsidios) por Trabajador
SELECT
    -- Datos de Identificación Persona (Hoja 1)
    P.pers_codigo     AS Codigo_Trabajador,
    P.pers_apelpat    AS Apellido_Paterno,
    P.pers_apelmat    AS Apellido_Materno,
    P.pers_nombre     AS Nombre,
    P.pers_dni        AS DNI_LE,
    P.pers_cargo      AS Cargo,
    P.pers_condicion  AS Condicion,
    P.pers_fechnac    AS Fecha_Nacimiento,
    P.pers_ingreso    AS Fecha_Ingreso,
    P.pers_afp        AS Fecha_AFP,
    P.pers_nom_afp    AS pers_nom_afp,
    P.pers_c_essal    AS C_ESSAL,

    -- Eventos
    EH.evhi_nom       AS Nombre_Evento,
    EHP.periodo       AS Periodo,
    EHP.mes           AS Mes,
    EHP.monto         AS Valor_Evento

FROM tb_persona_historica AS P
    INNER JOIN tb_evento_historico_persona AS EHP ON EHP.pers_id = P.pers_id
    INNER JOIN tb_evento_historico AS EH ON EH.evhi_id = EHP.evhi_id
WHERE EHP.periodo = 2026 AND EHP.mes = 2;
