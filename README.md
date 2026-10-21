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

## Frontend

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_URL debe apuntar al backend, por defecto http://127.0.0.1:8000/api

npm run dev
```

Abrir `http://localhost:5173`. La pantalla inicial muestra el estado de la
conexión con el backend (debe decir "Conexión OK").

## Variables de entorno

Ninguna credencial se commitea al repositorio. Cada `.env` tiene su propio
`.env.example` como referencia:

- `backend/.env.example`
- `frontend/.env.example`

## Estado del proyecto

Desarrollo incremental por etapas — ver el plan completo y las reglas de
negocio en [CLAUDE.md](CLAUDE.md).

- [x] Etapa 0 — Setup del proyecto
- [ ] Etapa 1 — Modelo de datos y autenticación
- [ ] Etapa 2 — CRUD de categorías
- [ ] Etapa 3 — CRUD de movimientos
- [ ] Etapa 4 — Dashboard MVP (resumen + gráfico por categoría)
- [ ] Etapa 5 — Presupuestos (iteración 2)
- [ ] Etapa 6 — Evolución mensual (iteración 2)
- [ ] Etapa 7 — Cierre y documentación final

## Uso de inteligencia artificial

Ver [IA_USO.md](IA_USO.md).
