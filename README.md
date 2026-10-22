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
- PostgreSQL 14+ (servidor corriendo y accesible)
- Git

> Si tu máquina no tiene permisos de administrador, podés instalar Node.js con
> [nvm](https://github.com/nvm-sh/nvm) y PostgreSQL con
> [Miniforge/conda-forge](https://github.com/conda-forge/miniforge) — ninguno
> de los dos requiere `sudo`. Ver el detalle de cómo se armó este entorno en
> [CLAUDE.md](CLAUDE.md#entorno-de-desarrollo-local).

## Backend

```bash
cd backend
python -m venv .venv          # o el entorno conda/virtualenv que prefieras
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Completar .env con:
# - DJANGO_SECRET_KEY (generar una propia, no reusar la de ejemplo)
# - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT de tu PostgreSQL local

python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Verificar que levantó bien:

```bash
curl http://127.0.0.1:8000/api/health/
# {"status":"ok","database":"ok"}
```

Si `database` no da `"ok"`, revisar que PostgreSQL esté corriendo y que las
credenciales en `.env` sean correctas.

### Usuario de prueba y autenticación (JWT)

No hay registro público de usuarios. Para desarrollo local se crea un único
usuario de prueba a partir de variables de entorno (nunca se commitean
credenciales):

```bash
# En backend/.env, completar:
# TEST_USER_USERNAME=...
# TEST_USER_PASSWORD=...
# TEST_USER_EMAIL=...

python manage.py seed_test_user
```

Con ese usuario podés pedir un token:

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
sembrado con `seed_test_user`); después de iniciar sesión vas a ver la
pantalla de Categorías.

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
- [ ] Etapa 3 — CRUD de movimientos
- [ ] Etapa 4 — Dashboard MVP (resumen + gráfico por categoría)
- [ ] Etapa 5 — Presupuestos (iteración 2)
- [ ] Etapa 6 — Evolución mensual (iteración 2)
- [ ] Etapa 7 — Cierre y documentación final

## Uso de inteligencia artificial

Ver [IA_USO.md](IA_USO.md).
