# Guía de Ejecución: ETL Migración de Planillas Excel a Scripts SQL

Este proyecto automatiza la extracción, transformación y generación de scripts SQL (`.sql`) por lotes e idempotentes para **PostgreSQL** a partir de archivos históricos de planillas en **Excel (`.xlsx`)**.

---

## 📋 Requisitos Previos

- **Python 3.10** o superior instalado en el sistema.
- Archivo Excel con las planillas (por defecto se busca en la raíz del proyecto o dentro de la carpeta `python`).

---

## 🐧 Guía de Ejecución en LINUX

### 1. Abrir la terminal y ubicarse en el directorio del script
Asegúrate de estar ubicado en la carpeta `python` del proyecto:
```bash
cd /ruta/hacia/Migraciones-xlxs-a-scripts-sql/python
```

### 2. Crear y activar el entorno virtual
Es una buena práctica aislar las dependencias:
```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activar según tu shell:
# En Bash / Zsh:
source .venv/bin/activate

# En Fish shell (si tu terminal usa fish):
source .venv/bin/activate.fish
```
*(Verás que la terminal ahora muestra el prefijo `(.venv)`).*

### 3. Instalar las dependencias
Instala las librerías necesarias (`pandas`, `openpyxl`):
```bash
pip install -r requirements.txt
```

### 4. Comando para ejecutar el script

Tienes dos formas de ejecutarlo:

#### Opción A: Modo Interactivo (Recomendado)
Ejecuta el script sin parámetros para que el asistente te guíe paso a paso:
```bash
python3 main.py
```

El script te preguntará secuencialmente:
1. **Archivo Excel:** Detectará automáticamente los archivos `.xlsx` en la carpeta o puedes escribir una ruta manual.
2. **Hoja:** Te listará las hojas disponibles (ej. `ENERO`, `FEBRERO`, etc.).
3. **Periodo / Año:** Año correspondiente (por defecto `2015`).
4. **Mes:** Número de mes del 1 al 12 (lo deduce automáticamente del nombre de la hoja).
5. **Esquema BD:** Esquema de PostgreSQL destino (por defecto `public`).
6. **Batch Size:** Cantidad de filas por bloque `INSERT` (por defecto `500`).
7. **Omitir montos en 0.0:** `s` o `N` (por defecto `N`).

#### Opción B: Modo por Argumentos (Línea de Comandos)
Si prefieres ejecutarlo directamente en una sola línea sin preguntas:
```bash
python3 main.py --excel "../PLANILLA PERSONAL 728 _ENERO 2015.xlsx" --sheet ENERO --periodo 2015 --mes 1
```

### 5. Esperar a que se ejecute el proceso
Una vez lanzado el comando, **espera a que el proceso complete sus 3 fases** en pantalla:

```text
-----------------------------------------------------------------
Iniciando procesamiento ETL con la siguiente configuración:
  • Archivo Excel : /ruta/al/archivo.xlsx
  • Hoja Target   : ENERO
  • Periodo / Mes : 2015 / 1
  • Esquema BD    : public
  • Batch Size    : 500
  • Skip 0.0      : False
-----------------------------------------------------------------

[1/3] Leyendo archivo Excel y analizando cabeceras...
      - Filas brutas válidas analizadas : 853
      - Trabajadores únicos con data   : 412
      - Columnas de eventos detectadas : 3
      - Columnas conceptos detectadas  : 52

[2/3] Generando script SQL idempotente y por lotes...

[3/3] ¡Proceso completado exitosamente!
      - Registros personas a insertar : 412
      - Registros eventos a insertar  : 1236
      - Registros conceptos a insertar: 21424
      - Archivo SQL generado         : /.../python/output_sql/insert_ENERO_2015_1.sql
      - Tamaño del archivo SQL       : 3.27 MB (3346.3 KB)
=================================================================
```

---

## 🪟 Guía de Ejecución en WINDOWS

### 1. Abrir la consola (CMD o PowerShell) y ubicarse en la carpeta
Abre **Símbolo del sistema (CMD)** o **PowerShell** y navega a la carpeta `python`:
```cmd
cd C:\ruta\a\Migraciones-xlxs-a-scripts-sql\python
```

### 2. Crear y activar el entorno virtual

#### En Símbolo del Sistema (CMD):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

#### En PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
> **Nota para PowerShell:** Si recibes el error `la ejecución de scripts está deshabilitada en este sistema`, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> Y luego vuelve a ejecutar `.venv\Scripts\Activate.ps1`.

### 3. Instalar las dependencias
```cmd
pip install -r requirements.txt
```

### 4. Comando para ejecutar el script

#### Opción A: Modo Interactivo (Recomendado)
```cmd
python main.py
```
Sigue las indicaciones numéricas en consola seleccionando el archivo y la hoja.

#### Opción B: Modo por Argumentos (CLI directo)
```cmd
python main.py --excel "..\PLANILLA PERSONAL 728 _ENERO 2015.xlsx" --sheet ENERO --periodo 2015 --mes 1
```

### 5. Esperar a que se ejecute el proceso
El script procesará los datos fila por fila y generará los bloques SQL. Espera pacientemente hasta ver el mensaje:
`[3/3] ¡Proceso completado exitosamente!`

---

## ⚙️ Tabla de Argumentos Disponibles

| Argumento | Tipo | Default | Descripción |
| :--- | :---: | :---: | :--- |
| `--excel` | `str` | *None* | Ruta al archivo Excel (`.xlsx`). Si se omite, activa el menú interactivo. |
| `--sheet` | `str` | *None* | Nombre de la pestaña u hoja a procesar (ej. `ENERO`, `FEBRERO`). |
| `--periodo` | `int` | `2015` | Año / periodo fiscal correspondiente a la planilla. |
| `--mes` | `int` | *Deducido* | Número de mes (1 al 12). Si no se indica, se infiere del nombre de la hoja. |
| `--schema` | `str` | `public` | Esquema destino en la base de datos PostgreSQL. |
| `--batch-size` | `int` | `500` | Cantidad de registros por bloque transaccional `INSERT`. |
| `--skip-empty-concepts` | flag | `False` | Si se incluye, descarta conceptos cuyo importe sea `0.0` o nulo. |

---

## 📁 Archivo SQL Resultante

Una vez finalizada la ejecución, el script SQL generado se almacena en la carpeta:
```text
python/output_sql/insert_<HOJA>_<PERIODO>_<MES>.sql
```
*(Por ejemplo: `python/output_sql/insert_ENERO_2015_1.sql`)*

### Características del SQL generado:
1. **Idempotente:** Crea automáticamente el esquema y las tablas si no existen (`IF NOT EXISTS`).
2. **Upsert seguro:** Inserta personas con `ON CONFLICT (pers_id) DO NOTHING`.
3. **Limpieza previa del periodo:** Elimina datos previos del mismo periodo y mes para permitir reejecuciones sin duplicar información.
4. **Ejecución por Lotes:** Agrupa inserciones en bloques envueltos en transacciones (`BEGIN; ... COMMIT;`) para máximo rendimiento y estabilidad.

---

## 🗄️ Cómo Ejecutar el SQL en PostgreSQL

Puedes ejecutar el archivo resultante directamente con `psql` o abrirlo en tu gestor de base de datos preferido (pgAdmin, DBeaver):

```bash
# Ejemplo usando psql en terminal:
psql -U tu_usuario -d tu_base_de_datos -h localhost -p 5432 -f output_sql/insert_ENERO_2015_1.sql
```
