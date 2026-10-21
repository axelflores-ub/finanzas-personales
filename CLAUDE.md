# CLAUDE.md

Convenciones y decisiones de este proyecto. Léelo antes de implementar cualquier etapa.

## Proyecto

Sistema Web de Gestión de Finanzas Personales — trabajo práctico de la materia
Prácticas de Laboratorio, Tecnicatura en Programación de Computadoras,
Universidad de Belgrano. Alumno: Axel Flores. Docente tutor: Mg. Ing. Guillermo
Ramiro Maquieira. Fecha de presentación: 26/11/2026.

## Stack tecnológico

- **Backend:** Python, Django, Django REST Framework.
- **Frontend:** Vue 3 (Composition API), Vite, Bootstrap 5, Axios.
- **Base de datos:** PostgreSQL.
- **Gráficos:** Chart.js.
- **Autenticación:** JWT (`djangorestframework-simplejwt`), sin registro público de
  usuarios por ahora (un único usuario creado manualmente).
- **Control de versiones:** Git y GitHub.

## Arquitectura

```
Vue 3 SPA (Vite, puerto 5173)
   │  Axios + JWT
   ▼
Django REST Framework (puerto 8000)
   │  ORM
   ▼
PostgreSQL
```

- Backend y frontend viven en carpetas separadas (`backend/`, `frontend/`) dentro
  de un mismo repositorio.
- El backend se organiza en apps de Django por dominio, bajo `backend/apps/`
  (`core`, y luego `categorias`, `movimientos`, `presupuestos`, `dashboard`).
- CORS está restringido únicamente a los orígenes de desarrollo autorizados
  (ver `CORS_ALLOWED_ORIGINS` en `backend/.env`).
- No hay tabla de moneda: todos los montos se asumen en **ARS**. Si se necesitara
  multi-moneda a futuro, se agregaría un campo `moneda` sin romper el modelo
  actual.

## Reglas de negocio vigentes

- Un usuario solo puede ver/editar/eliminar sus propios recursos.
- Las categorías asignadas a movimientos y presupuestos deben pertenecer siempre
  al usuario autenticado (se valida en el serializer, no solo en el frontend).
- `Categoria`: único por (`usuario`, `nombre`, `tipo`).
- Los montos usan `DecimalField`, nunca `float`.
- No se puede eliminar una categoría con movimientos o presupuestos asociados
  (`on_delete=PROTECT`).

## Metodología de trabajo

- Desarrollo **incremental**, por etapas. Cada etapa se trabaja como una
  funcionalidad completa: backend + frontend + integración + pruebas, antes de
  pasar a la siguiente.
- No se avanza a la siguiente etapa sin confirmación explícita del alumno.
- **MVP (Iteración 1):** login, categorías, CRUD de movimientos, dashboard con
  ingresos/gastos/balance y gráfico de gastos por categoría.
- **Iteración 2:** presupuestos mensuales con % utilizado, gráfico de evolución
  mensual.
- Se evita agregar funcionalidades o dependencias no pedidas en el alcance
  aprobado.

## Convenciones de código

- Nombres de dominio (modelos, campos) en español, consistentes con la
  documentación de la cátedra.
- Backend: apps chicas por dominio, serializers con validaciones explícitas de
  pertenencia y de reglas de negocio (no confiar solo en constraints de DB).
- Frontend: composables/servicios en `src/api/` por recurso, vistas en
  `src/views/`, componentes reutilizables en `src/components/<dominio>/`.
- Variables de entorno vía `.env` (nunca hardcodeadas ni commiteadas). Cada
  `.env` tiene su `.env.example` correspondiente.

## Entorno de desarrollo local

Esta máquina no tiene permisos de administrador (`sudo`), por lo que todo el
entorno se instaló sin privilegios de admin:

- **Node.js:** instalado vía `nvm` (`~/.nvm`).
- **Python + PostgreSQL:** instalados vía Miniforge/conda-forge
  (`~/miniforge3`), entorno conda `finanzas` (Python 3.12, PostgreSQL 16).
- El servidor PostgreSQL corre localmente con los datos en
  `~/.local/share/postgres-finanzas`, arrancado manualmente con `pg_ctl`
  (no es un servicio del sistema).

Ver [README.md](README.md) para los pasos de instalación y ejecución.

## Uso de inteligencia artificial

Este proyecto se desarrolla con asistencia de Claude Code (Anthropic). El uso de
IA se documenta en `IA_USO.md`, como pide la cátedra ("es posible el uso, no
abuso, especificando las herramientas utilizadas").
