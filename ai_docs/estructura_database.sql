create table tb_concepto_historico
(
    cohi_id       bigserial
        primary key,
    cohi_tipo     varchar,
    cohi_cod      varchar,
    cohi_nom      varchar,
    cohi_estado   varchar,
    usu_info      jsonb,
    fecha_created timestamp with time zone default now()
);

alter table tb_concepto_historico
    owner to postgres;

create table tb_persona_historica
(
    pers_id        bigserial
        primary key,
    pers_nombre    text,
    pers_apelpat   text,
    pers_apelmat   text,
    pers_fechnac   date,
    pers_ingreso   date,
    pers_cargo     text,
    pers_condicion varchar,
    pers_afp       date,
    pers_nom_afp   varchar,
    pers_c_essal   varchar,
    pers_dni       varchar(8),
    pers_codigo    varchar,
    pers_estado    varchar(1),
    usu_info       jsonb,
    fecha_created  timestamp with time zone default now()
);

alter table tb_persona_historica
    owner to postgres;

comment on column tb_persona_historica.pers_afp is 'Fecha de Afiliacion AFP (Columna 6 Hoja 1: Fecha Afiliacion AFP / Alias export: Fecha_AFP)';
comment on column tb_persona_historica.pers_nom_afp is 'Nombre de la AFP (Columna 9 Hoja 1: Nombre AFP / Alias export: pers_nom_afp)';
comment on column tb_persona_historica.pers_c_essal is 'Codigo Autogenerado EsSalud (Columna 8 Hoja 1: C.ESSAL. / Alias export: C_ESSAL)';

create table tb_concepto_historico_persona
(
    pers_cohi_id  bigserial
        primary key,
    periodo       integer,
    mes           integer,
    pers_id       integer
        references tb_persona_historica (pers_id),
    cohi_id       integer
        references tb_concepto_historico (cohi_id),
    monto         double precision,
    estado        varchar,
    usu_info      jsonb,
    fecha_created timestamp with time zone default now()
);

alter table tb_concepto_historico_persona
    owner to postgres;

create table tb_evento_historico
(
    evhi_id       bigserial
        primary key,
    evhi_nom      text,
    evhi_tipo     integer,
    evhi_estado   varchar,
    usu_info      jsonb,
    fecha_created timestamp with time zone default now()
);

alter table tb_evento_historico
    owner to postgres;

create table tb_evento_historico_persona
(
    pers_evhi_id  bigserial
        primary key,
    periodo       integer,
    mes           integer,
    pers_id       integer
        references tb_persona_historica (pers_id),
    evhi_id       integer
        references tb_evento_historico (evhi_id),
    monto         varchar,
    estado        varchar,
    usu_info      jsonb,
    fecha_created timestamp with time zone default now()
);

alter table tb_evento_historico_persona
    owner to postgres;