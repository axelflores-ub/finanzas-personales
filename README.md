# Sistema Web de Gestión de Finanzas Personales

Trabajo práctico de la materia Prácticas de Laboratorio — Tecnicatura en
Programación de Computadoras, Universidad de Belgrano.

Aplicación web para registrar ingresos y gastos, clasificarlos por categorías,
y visualizar un dashboard con balance mensual y gráficos.

## Stack

Python · Django · Django REST Framework · PostgreSQL · Vue 3 · Vite ·
Bootstrap 5 · Axios · Chart.js

## Requisitos

- Python 3.11+
- Node.js 20+ (LTS)
- PostgreSQL 14+
- Git

Esta guía cubre dos escenarios:

- **[A] Tenés una máquina "normal"**, con permisos de administrador y
  PostgreSQL instalado (Homebrew, Postgres.app, el instalador oficial, o ya
  corriendo como servicio).
- **[B] No tenés permisos de administrador** (`sudo`) — el escenario real en
  el que se desarrolló este proyecto: una Mac sin acceso admin, con Node.js
  instalado vía [nvm](https://github.com/nvm-sh/nvm) y Python+PostgreSQL vía
  [Miniforge/conda-forge](https://github.com/conda-forge/miniforge), ninguno
  de los dos requiere `sudo`. Más contexto en
  [CLAUDE.md](CLAUDE.md#entorno-de-desarrollo-local).

Seguí la sección que te corresponda y después continuá en
["Crear el rol y la base de datos"](#crear-el-rol-y-la-base-de-datos), que es
igual para ambos casos.

### [A] PostgreSQL ya instalado con permisos de administrador

Confirmá que el servidor esté corriendo y que tengas el cliente `psql`:

```bash
psql --version
pg_isready            # debe responder "accepting connections"
```

Si no tenés PostgreSQL instalado: `brew install postgresql@16 && brew services start postgresql@16`
(Homebrew) o descargalo de [postgresql.org](https://www.postgresql.org/download/).
Luego seguí directo a ["Crear el rol y la base de datos"](#crear-el-rol-y-la-base-de-datos).

### [B] Sin permisos de administrador (Node vía nvm, Python+PostgreSQL vía Miniforge)

```bash
# 1. Node.js, sin sudo
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# Si es la primera vez que instalás nvm, cerrá y reabrí la terminal (o seguí
# las instrucciones que imprime el instalador) antes de continuar.
nvm install --lts

# 2. Python + PostgreSQL, sin sudo, vía Miniforge/conda-forge
curl -L -o Miniforge3.sh \
  "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
bash Miniforge3.sh -b -p "$HOME/miniforge3"
"$HOME/miniforge3/bin/conda" create -n finanzas python=3.12 postgresql=16 -c conda-forge -y

# 3. Activar el entorno en cada terminal nueva que uses para este proyecto
source "$HOME/miniforge3/bin/activate" finanzas

# 4. Inicializar y arrancar PostgreSQL como proceso de usuario (no como
#    servicio del sistema, porque no hay permisos para registrar uno)
initdb -D "$HOME/.local/share/postgres-finanzas" -U postgres -A trust -E UTF8
mkdir -p "$HOME/.local/share/postgres-logs"
pg_ctl -D "$HOME/.local/share/postgres-finanzas" \
  -l "$HOME/.local/share/postgres-logs/postgres.log" \
  -o "-p 5432 -k /tmp" start
```

`pg_ctl ... start` solo hace falta correrlo una vez por sesión/reinicio de la
máquina — si ya corriste `initdb`, en la siguiente terminal alcanza con
`source .../activate finanzas` y `pg_ctl -D ... start` (sin `initdb` de
nuevo). Para pararlo: `pg_ctl -D "$HOME/.local/share/postgres-finanzas" stop`.

### Crear el rol y la base de datos

Con PostgreSQL corriendo (cualquiera de los dos casos), creá el rol y la
base que va a usar la app. Reemplazá `elegí-una-contraseña-local` por una
contraseña propia — **no uses una contraseña real/reusada, es solo para tu
Postgres local**:

```bash
# Caso [A] (instalación normal, usuario de PostgreSQL con permisos para crear roles):
psql postgres -c "CREATE ROLE finanzas_user WITH LOGIN PASSWORD 'elegí-una-contraseña-local';"
psql postgres -c "CREATE DATABASE finanzas_db OWNER finanzas_user;"
psql postgres -c "ALTER ROLE finanzas_user CREATEDB;"   # necesario para correr los tests

# Caso [B] (Miniforge, servidor propio con el rol "postgres" de superusuario):
psql -h localhost -p 5432 -U postgres -c "CREATE ROLE finanzas_user WITH LOGIN PASSWORD 'elegí-una-contraseña-local';"
psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE finanzas_db OWNER finanzas_user;"
psql -h localhost -p 5432 -U postgres -c "ALTER ROLE finanzas_user CREATEDB;"
```

El `ALTER ROLE ... CREATEDB` es necesario porque `python manage.py test`
crea y destruye una base de datos de test (`test_finanzas_db`) en cada
corrida; sin ese permiso, la suite de tests falla al arrancar.

Verificar que quedó accesible:

```bash
psql -h localhost -p 5432 -U finanzas_user -d finanzas_db -c "SELECT 1;"
```

## Backend

```bash
cd backend
python -m venv .venv          # o `conda create -n finanzas python=3.12 ...` si usaste Miniforge arriba
source .venv/bin/activate      # o `source "$HOME/miniforge3/bin/activate" finanzas`
pip install -r requirements.txt

cp .env.example .env
```

Completá `backend/.env`:

- `DJANGO_SECRET_KEY`: generá una propia, no reuses la del ejemplo —
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  (podés correrlo recién después de `pip install -r requirements.txt`).
- `DB_NAME=finanzas_db`, `DB_USER=finanzas_user`, `DB_PASSWORD=` la que elegiste
  arriba, `DB_HOST=localhost`, `DB_PORT=5432`.
- `TEST_USER_USERNAME` / `TEST_USER_PASSWORD` / `TEST_USER_EMAIL`: el único
  usuario de la app (no hay registro público) — elegí los valores que
  quieras, no son credenciales reales de nadie.

Migrar y crear el usuario inicial:

```bash
python manage.py migrate
python manage.py seed_test_user
python manage.py runserver 127.0.0.1:8000
```

Verificar que levantó bien:

```bash
curl http://127.0.0.1:8000/api/health/
# {"status":"ok","database":"ok"}
```

Si `database` no da `"ok"`, revisar que PostgreSQL esté corriendo
(`pg_isready`, o `pg_ctl -D ... status` en el caso [B]) y que las
credenciales en `.env` coincidan con las del rol que creaste.

### Autenticación (JWT)

No hay registro público de usuarios — el único usuario es el que creaste
arriba con `seed_test_user`. Con ese usuario podés pedir un token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tu-usuario", "password": "tu-contraseña"}'
# {"access": "...", "refresh": "..."}

curl http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <access>"
# {"username": "...", "email": "..."}

curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh>"}'
```

Todos los endpoints son privados (`IsAuthenticated`) excepto `/api/health/`,
`/api/auth/token/` y `/api/auth/token/refresh/`.

### Categorías

CRUD completo, scopeado al usuario autenticado (`request.user`, nunca al
usuario que venga en el body):

```bash
GET    /api/categorias/          # listar las propias
POST   /api/categorias/          # crear ({"nombre": "...", "tipo": "INGRESO"|"GASTO"})
GET    /api/categorias/{id}/
PATCH  /api/categorias/{id}/
DELETE /api/categorias/{id}/     # 409 si tiene movimientos o presupuestos asociados
```

Todas requieren `Authorization: Bearer <access>`. Intentar acceder a una
categoría de otro usuario devuelve `404` (no se revela que existe).

### Movimientos

CRUD completo, scopeado al usuario autenticado. El `tipo` (INGRESO/GASTO) no
se manda ni se guarda: se deriva de `categoria.tipo` y viene de regalo en las
respuestas.

```bash
GET    /api/movimientos/         # listar los propios, más recientes primero
POST   /api/movimientos/         # {"categoria": id, "monto": "1500.00", "fecha": "2026-10-15", "descripcion": "..."}
GET    /api/movimientos/{id}/
PATCH  /api/movimientos/{id}/
DELETE /api/movimientos/{id}/
```

Filtros combinables por query params (`GET /api/movimientos/?...`):

| Parámetro | Ejemplo | Notas |
|---|---|---|
| `fecha_desde` | `2026-10-01` | `400` si el formato no es `YYYY-MM-DD` o la fecha no existe |
| `fecha_hasta` | `2026-10-31` | ídem; `400` si `fecha_desde > fecha_hasta` |
| `tipo` | `INGRESO` o `GASTO` | `400` si no es uno de esos dos valores |
| `categoria` | `3` | id numérico; `400` si no es numérico (si es numérico pero no existe o es de otro usuario, devuelve lista vacía, no error) |

La categoría debe pertenecer al usuario autenticado (`400` si no) y el monto
debe ser mayor a 0 (`400` si no). Igual que con categorías, acceder a un
movimiento ajeno por id da `404`.

### Dashboard

Dos endpoints de solo lectura, agregados con el ORM (`Sum`) sobre los
movimientos del usuario autenticado — no hay tablas ni resultados
precalculados. `mes` y `anio` son obligatorios en ambos; si faltan, no son
numéricos o están fuera de rango (`mes` 1-12, `anio` 2000-2100), devuelven
`400` con el detalle del parámetro inválido. Todos los importes viajan como
string decimal (`"1500.00"`), nunca `float`.

**`GET /api/dashboard/resumen/?mes=10&anio=2026`**

```json
{
  "mes": 10,
  "anio": 2026,
  "ingresos": "150000.00",
  "gastos": "13000.75",
  "balance": "136999.25"
}
```

**`GET /api/dashboard/gastos-por-categoria/?mes=10&anio=2026`**

```json
{
  "mes": 10,
  "anio": 2026,
  "total_gastos": "13000.75",
  "categorias": [
    {
      "categoria_id": 4,
      "categoria_nombre": "Alimentación",
      "monto": "9200.75",
      "porcentaje": "70.77"
    },
    {
      "categoria_id": 5,
      "categoria_nombre": "Transporte",
      "monto": "3800.00",
      "porcentaje": "29.23"
    }
  ]
}
```

Sin movimientos en el período: `resumen` devuelve los tres totales en
`"0.00"`; `gastos-por-categoria` devuelve `"total_gastos": "0.00"` y
`"categorias": []`. Una categoría de gasto sin movimientos en el período
simplemente no aparece en `categorias` (no se manda con monto 0).

**`GET /api/dashboard/presupuestos-resumen/?mes=10&anio=2026`** — separado de
`resumen`: acá `gasto_real_presupuestado` solo suma categorías que tienen un
presupuesto en el período (no el gasto general de `resumen.gastos`).

```json
{
  "mes": 10,
  "anio": 2026,
  "presupuesto_total": "150000.00",
  "gasto_real_presupuestado": "90000.00",
  "porcentaje_utilizado": "60.00"
}
```

**`GET /api/dashboard/evolucion-mensual/?anio=2026`** — siempre devuelve los
12 meses del año (1 a 12), con `"0.00"` en los que no tienen movimientos.

```json
{
  "anio": 2026,
  "meses": [
    { "mes": 1, "ingresos": "0.00", "gastos": "0.00", "balance": "0.00" },
    { "mes": 2, "ingresos": "0.00", "gastos": "0.00", "balance": "0.00" },
    { "mes": 10, "ingresos": "150000.00", "gastos": "13000.75", "balance": "136999.25" },
    { "mes": 12, "ingresos": "0.00", "gastos": "0.00", "balance": "0.00" }
  ]
}
```

### Presupuestos

CRUD completo sobre el modelo `Presupuesto` ya existente (Etapa 1), scopeado
al usuario autenticado. `gasto_real`, `porcentaje_utilizado` y `restante` se
calculan **en cada request** con `Sum`/`Decimal` sobre `Movimiento` — no se
guardan en la base, así que siempre reflejan los movimientos actuales sin
necesidad de señales ni recálculos manuales.

```bash
GET    /api/presupuestos/              # listar los propios (filtra ?mes=&anio= si se pasan)
POST   /api/presupuestos/              # {"categoria": id, "mes": 10, "anio": 2026, "monto_limite": "150000.00"}
GET    /api/presupuestos/{id}/
PATCH  /api/presupuestos/{id}/
DELETE /api/presupuestos/{id}/
```

Respuesta de cada presupuesto:

```json
{
  "id": 1,
  "categoria": 4,
  "categoria_nombre": "Alimentación",
  "mes": 10,
  "anio": 2026,
  "monto_limite": "150000.00",
  "gasto_real": "90000.00",
  "porcentaje_utilizado": "60.00",
  "restante": "60000.00",
  "creado_en": "2026-10-24T17:37:23.767395-03:00"
}
```

Reglas: la categoría debe ser del usuario autenticado y de tipo `GASTO`
(`400` si no); único por (`usuario`, `categoria`, `mes`, `anio`) (`400` si
duplicado); `monto_limite` > 0 (`400` si no). Si el gasto supera el límite,
`porcentaje_utilizado` puede superar `100` y `restante` da negativo (lo
usa el frontend para mostrar "Excedido en $X" en vez de un número negativo
confuso).

### Pruebas automatizadas

```bash
python manage.py test apps
```

## Frontend

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_URL debe apuntar al backend, por defecto http://127.0.0.1:8000/api

npm run dev
```

Abrir `http://localhost:5173`. Te va a pedir login (usá el usuario de prueba
sembrado con `seed_test_user`); después de iniciar sesión vas a ver el
**Dashboard** (resumen del mes actual, gráfico de gastos por categoría,
gráfico de evolución mensual ingresos vs. gastos del año, y mini-resumen de
presupuestos). Desde el menú lateral también se accede a **Categorías**,
**Movimientos** y **Presupuestos** (límites de gasto por categoría, con
barra de progreso: verde <80%, amarillo 80-99%, rojo ≥100%).

### Sesión: qué se guarda y qué limitación tiene

El access y el refresh token viven **solo en memoria** (estado de Pinia), no
en `localStorage` ni `sessionStorage`. Esto evita que un ataque XSS pueda
robar un token persistido. La contrapartida, asumida conscientemente para
este MVP: **recargar la página (F5) cierra la sesión** — no hay nada que
rehidratar. Si una request responde `401` y el refresh también falla (token
vencido o inválido), la app cierra la sesión y redirige a `/login` con un
aviso.

## Variables de entorno

Ninguna credencial se commitea al repositorio. Cada `.env` tiene su propio
`.env.example` como referencia:

- `backend/.env.example`
- `frontend/.env.example`

## Estado del proyecto

Desarrollo incremental por etapas — ver el plan completo y las reglas de
negocio en [CLAUDE.md](CLAUDE.md).

- [x] Etapa 0 — Setup del proyecto
- [x] Etapa 1 — Modelo de datos y autenticación
- [x] Etapa 2 — CRUD de categorías e interfaz Vue
- [x] Etapa 3 — CRUD de movimientos financieros
- [x] Etapa 4 — Dashboard financiero MVP (resumen + gráfico por categoría)
- [x] Etapa 5 — Presupuestos mensuales
- [x] Etapa 6 — Evolución mensual de ingresos y gastos
- [ ] Etapa 7 — Cierre y documentación final

## Uso de inteligencia artificial

Ver [IA_USO.md](IA_USO.md).
