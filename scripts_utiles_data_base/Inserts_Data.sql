INSERT INTO tb_evento_historico (evhi_nom, evhi_tipo, evhi_estado, usu_info)
VALUES
    ('D. TRABJ.',        1, 'A', NULL), -- ID 1: Días trabajados (ej. 30, 0)
    ('DOMINIC.',         1, 'A', NULL), -- ID 2: Dominicales (ej. 4)
    ('VACACIONES',      2, 'A', NULL), -- ID 3: Indicador SI / NO
    ('SUS / SAN',       2, 'A', NULL), -- ID 4: Suspensión / Sanción (SI / NO)
    ('LIC. SIN.',       2, 'A', NULL), -- ID 5: Licencia Sindical (SI / NO)
    ('LIC.S/GO.',        2, 'A', NULL), -- ID 6: Licencia sin goce (SI / NO)
    ('SUBSID.E INFERM.', 2, 'A', NULL); -- ID 7: Subsidio por enfermedad (SI / NO)



INSERT INTO tb_concepto_historico (cohi_tipo, cohi_cod, cohi_nom, cohi_estado, usu_info)
VALUES
    -- ==========================================
    -- 1. REGISTROS ORIGINALES (IDs 1 al 38)
    -- ==========================================
    -- Ganancias originales (17)
    ('G', '01', 'BASICO',   'A', NULL), -- ID 1
    ('G', '02', 'R. PERS',  'A', NULL), -- ID 2
    ('G', '04', 'B. FAMI',  'A', NULL), -- ID 3
    ('G', '07', 'DOMI',     'A', NULL), -- ID 4
    ('G', '09', '7.5% R.',  'A', NULL), -- ID 5
    ('G', '13', 'R.M. 149', 'A', NULL), -- ID 6
    ('G', '16', 'REINT.',   'A', NULL), -- ID 7
    ('G', '21', 'GRAT. V.', 'A', NULL), -- ID 8
    ('G', '25', 'FERIAD',   'A', NULL), -- ID 9
    ('G', '35', 'REF. MO',  'A', NULL), -- ID 10
    ('G', '37', '15% DE',   'A', NULL), -- ID 11
    ('G', '42', 'FUN. MU',  'A', NULL), -- ID 12
    ('G', '45', '15% R.V.', 'A', NULL), -- ID 13
    ('G', '49', 'REDOND',   'A', NULL), -- ID 14
    ('G', '50', 'INCREM',   'A', NULL), -- ID 15
    ('G', '28', 'I.C.V.',   'A', NULL), -- ID 16
    ('G', '29', 'R. FAM.',  'A', NULL), -- ID 17

    -- Descuentos originales (17)
    ('D', '53', 'S.N.P.',   'A', NULL), -- ID 18
    ('D', '56', 'ADELAN',   'A', NULL), -- ID 19
    ('D', '57', 'RETJU',    'A', NULL), -- ID 20
    ('D', '59', 'MULTAS',   'A', NULL), -- ID 21
    ('D', '60', 'CAFAE',    'A', NULL), -- ID 22
    ('D', '88', '+ VIDA',   'A', NULL), -- ID 23
    ('D', '90', 'SIND. O',  'A', NULL), -- ID 24
    ('D', '58', 'AD. SNP',  'A', NULL), -- ID 25
    ('D', '80', 'IMP. RE.', 'A', NULL), -- ID 26
    ('D', '81', 'IFP. RE.', 'A', NULL), -- ID 27
    ('D', '64', 'APORTE',   'A', NULL), -- ID 28
    ('D', '72', 'SEGURO',   'A', NULL), -- ID 29
    ('D', '76', 'COM. MI',  'A', NULL), -- ID 30
    ('D', '82', 'C.V.R.',   'A', NULL), -- ID 31
    ('D', '84', 'C.A.M.',   'A', NULL), -- ID 32
    ('D', '95', 'DES. IN',  'A', NULL), -- ID 33
    ('D', '99', 'DESC. F',  'A', NULL), -- ID 34

    -- Contribuciones Patronales / Aportes originales (4)
    ('A', NULL, 'ESSA',     'A', NULL), -- ID 35
    ('A', NULL, 'SNP',      'A', NULL), -- ID 36
    ('A', NULL, 'SCTR',     'A', NULL), -- ID 37
    ('A', NULL, 'IES',      'A', NULL), -- ID 38

    -- ==========================================
    -- 2. REGISTROS FALTANTES (IDs 39 al 45)
    -- ==========================================
    -- Ganancias faltantes (4)
    ('G', '14', 'BON. EX',  'A', NULL), -- ID 39
    ('G', '20', 'REIN.V',   'A', NULL), -- ID 40
    ('G', '46', 'RE. BON',  'A', NULL), -- ID 41
    ('G', '47', 'REI. BO',  'A', NULL), -- ID 42

    -- Descuentos faltantes (3)
    ('D', '65', 'ANT. XR',  'A', NULL), -- ID 43
    ('D', '67', 'DSCT. M',  'A', NULL), -- ID 44
    ('D', '68', 'SEGUR.',   'A', NULL); -- ID 45