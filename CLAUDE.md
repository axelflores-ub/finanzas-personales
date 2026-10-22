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
  usuarios por ahora. El único usuario se crea/actualiza con
  `python manage.py seed_test_user`, que lee `TEST_USER_USERNAME` /
  `TEST_USER_PASSWORD` / `TEST_USER_EMAIL` desde `backend/.env` (nunca se
  commitea una contraseña).
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
- El backend se organiza en apps de Django por dominio, bajo `backend/apps/`:
  `core` (infraestructura: health check, auth JWT), `categorias`,
  `movimientos`, `presupuestos` y, en Etapa 4, `dashboard`.
- CORS está restringido únicamente a los orígenes de desarrollo autorizados
  (ver `CORS_ALLOWED_ORIGINS` en `backend/.env`).
- No hay tabla de moneda: todos los montos se asumen en **ARS**. Si se necesitara
  multi-moneda a futuro, se agregaría un campo `moneda` sin romper el modelo
  actual.
- `IsAuthenticated` es el permiso por defecto de DRF. Los únicos endpoints
  públicos son `/api/health/`, `/api/auth/token/` y
  `/api/auth/token/refresh/`.

## Modelo de datos (Etapa 1)

- **`Categoria`** (`apps/categorias`): `usuario` (FK→User, `CASCADE`),
  `nombre`, `tipo` (`INGRESO`/`GASTO`), `creado_en`. Único por
  (`usuario`, `nombre`, `tipo`).
- **`Movimiento`** (`apps/movimientos`): `usuario` (FK→User, `CASCADE`),
  `categoria` (FK→Categoria, `PROTECT`), `monto` (`DecimalField`, 2 decimales,
  > 0), `fecha`, `descripcion` (opcional). El tipo del movimiento se infiere de
  `categoria.tipo`, no se duplica.
- **`Presupuesto`** (`apps/presupuestos`): `usuario` (FK→User, `CASCADE`),
  `categoria` (FK→Categoria, `PROTECT`, debe ser tipo `GASTO`), `mes`, `anio`,
  `monto_limite` (`DecimalField`, > 0). Único por
  (`usuario`, `categoria`, `mes`, `anio`).
- La pertenencia de `categoria` al `usuario`, y la restricción de tipo `GASTO`
  en `Presupuesto`, se validan en `clean()` de cada modelo (defensa en
  profundidad: se van a repetir en los serializers cuando lleguen los
  endpoints CRUD en la Etapa 2/3).

## API y frontend de Categorías (Etapa 2)

- `CategoriaViewSet` (`apps/categorias/views.py`) es un `ModelViewSet`
  estándar; `get_queryset()` siempre filtra por `usuario=request.user` — así
  un `GET/PATCH/DELETE /api/categorias/{id}/` sobre una categoría ajena da
  `404` (nunca `403`, para no confirmar que el recurso existe).
- `usuario` **no es un campo del serializer**: no se puede mandar desde el
  body. Se asigna en `CategoriaSerializer.create()` desde
  `self.context["request"].user`.
- La unicidad (`usuario`, `nombre`, `tipo`) se valida explícitamente en
  `CategoriaSerializer.validate()` (no se usa el auto-`UniqueTogetherValidator`
  de DRF porque `usuario` no es un campo visible del serializer).
- Borrar una categoría en uso devuelve `409 Conflict` con
  `{"detail": "..."}` (se captura `ProtectedError` en el `destroy()` del
  viewset), no un 500 ni un 400.
- **Frontend — sesión en memoria, no persistida:** `store/auth.js` (Pinia)
  guarda `accessToken`/`refreshToken` solo en el estado de la store, nunca en
  `localStorage`/`sessionStorage`. Decisión consciente para este MVP:
  minimiza superficie de robo de token vía XSS, a costa de que recargar la
  página cierra la sesión. Documentado también en el README.
- **Frontend — dos clientes Axios:** `api/authClient.js` (sin interceptores,
  usado solo por el store para login/refresh/me) y `api/axios.js` (con
  interceptores de request —agrega el Bearer token— y de response —si hay
  `401`, intenta refrescar una vez; si falla, desloguea y redirige a
  `/login`—). Separarlos evita una dependencia circular
  (`axios.js` → `store/auth.js` → `axios.js`) y evita que un refresh fallido
  dispare otro refresh en bucle.
- **Frontend — modales sin JS de Bootstrap:** los diálogos (`ConfirmDialog`,
  `CategoriaFormModal`) reusan las clases CSS de Bootstrap pero se togglean
  con `v-if` de Vue, sin importar `bootstrap.bundle.js` ni Popper. Menos
  dependencias y evita pelear el DOM imperativo de Bootstrap con la
  reactividad de Vue.

## API y frontend de Movimientos (Etapa 3)

- `MovimientoSerializer` expone `tipo` y `categoria_nombre` como campos
  **read-only** derivados de `categoria.tipo`/`categoria.nombre`
  (`source="categoria.tipo"`): el modelo no duplica el tipo, pero la API
  igual lo devuelve listo para mostrar sin que el frontend tenga que cruzar
  dos listas.
- La pertenencia de `categoria` al usuario se valida en
  `MovimientoSerializer.validate_categoria()`, mismo patrón que en
  `CategoriaSerializer`.
- **Filtros implementados a mano en `MovimientoViewSet.get_queryset()`, sin
  `django-filter`.** Se evaluó usarlo, pero su comportamiento por defecto
  ante un parámetro inválido es ignorarlo o devolver queryset vacío en
  silencio, no un `400` — y necesitábamos mensajes de error explícitos para
  fecha inválida, tipo inválido y rango `fecha_desde > fecha_hasta`. Filtrar
  a mano con `rest_framework.exceptions.ValidationError` da control total
  sobre esos mensajes sin sumar una dependencia. `django-filter` se sacó de
  `requirements.txt`.
  - Ojo con `django.utils.dateparse.parse_date`: ante una fecha
    sintácticamente válida pero imposible (`"2026-99-99"`) no devuelve
    `None`, **lanza `ValueError`** al construir el `date`. Hay que
    envolverlo en `try/except`, si no el request explota con 500 en vez de
    devolver el 400 esperado.
- `categoria` como filtro: si el id no es numérico, `400`. Si es numérico
  pero no existe o es de otro usuario, lista vacía (no se revela si existe).
- **Frontend — formato de moneda:** `src/utils/format.js` arma
  `"$ 25.000,00"` a mano (prefijo `"$ "` + `Intl.NumberFormat('es-AR')`), no
  con `Intl...{style:'currency'}`, porque ese formato varía el símbolo/espacio
  según el entorno (ICU) y queríamos el resultado exacto pedido.
- **Frontend — selector de categoría dependiente del tipo:** tanto el
  formulario de alta/edición como la barra de filtros filtran las categorías
  disponibles según el tipo elegido (`INGRESO`/`GASTO`), y si no hay
  categorías de ese tipo el formulario lo avisa y deshabilita "Guardar" en
  vez de dejar guardar con la categoría vacía.
- **Bug real encontrado en la verificación manual de esta etapa** (corregido
  antes del commit): al abrir "Nuevo movimiento" por primera vez, el tipo por
  defecto (`GASTO`) no cambiaba de valor, así que el `watch` que
  auto-selecciona la primera categoría disponible nunca disparaba —
  `categoriaId` quedaba en `''` aunque el `<select>` mostrara visualmente la
  única opción (comportamiento nativo del navegador, no de Vue). Se mandaba
  `categoria: ""` y el backend respondía 400. Fix en
  `MovimientoFormModal.vue`: calcular la categoría por defecto explícitamente
  al abrir el modal, no solo reaccionar a cambios de `tipo`.

## API y frontend de Dashboard (Etapa 4)

- `apps/dashboard` no tiene modelos: son dos vistas de solo lectura
  (`resumen`, `gastos_por_categoria`) que agregan sobre `Movimiento` con
  `Sum` del ORM. Sin tablas ni resultados precalculados, como pide el
  alcance — se recalculan en cada request.
- `mes`/`anio` se validan a mano en `apps/dashboard/validators.py`
  (`parse_periodo`), compartido por ambas vistas: obligatorios, enteros,
  `mes` 1-12, `anio` 2000-2100. Mismo criterio que los filtros de
  movimientos — `400` explícito en vez de fallar en silencio.
- Todo cálculo usa `Decimal` de punta a punta (incluido el porcentaje:
  `Decimal / Decimal * 100`, nunca se castea a `float`). Las respuestas
  serializan los montos como **string** (`"150000.00"`), no como número
  JSON, para que no haya ambigüedad de precisión del lado del cliente —
  mismo criterio que `monto` en `Movimiento`.
- `gastos_por_categoria` arma la lista a partir de
  `.values("categoria_id", "categoria__nombre").annotate(total=Sum("monto"))`:
  una categoría de gasto sin movimientos en el período simplemente no genera
  fila en el `GROUP BY`, así que no aparece en la respuesta (no se filtra
  después "a mano").
- **Frontend — Chart.js sin wrapper:** se usa la librería directa
  (`new Chart(canvasRef.value, {...})`) en vez de `vue-chartjs`, con un
  `<canvas>` referenciado por `ref` de Vue. El ciclo de vida se maneja a
  mano: `destruirChart()` antes de cada recreación y en `onBeforeUnmount`,
  para no dejar instancias huérfanas ni pelear el "Canvas is already in
  use" de Chart.js cuando el `v-if` del estado vacío desmonta el `<canvas>`.
  Se optó por destruir y recrear en cada cambio de período en vez de
  `chart.update()` in-place: con pocas categorías el costo es insignificante
  y el código queda más simple/predecible.
- **Dashboard es la pantalla por defecto tras el login:** el redirect raíz
  del router (`/` y el fallback de `LoginView` sin `redirect` en la query)
  apunta a `{ name: 'dashboard' }` en vez de `categorias`.

## Reglas de negocio vigentes

- Un usuario solo puede ver/editar/eliminar sus propios recursos.
- Las categorías asignadas a movimientos y presupuestos deben pertenecer siempre
  al usuario autenticado (validado en `clean()` del modelo; se repite en el
  serializer cuando exista).
- `Categoria`: único por (`usuario`, `nombre`, `tipo`).
- Los montos usan `DecimalField` (2 decimales), nunca `float`, y deben ser > 0
  (`MinValueValidator` + `CheckConstraint` en la base).
- Un `Presupuesto` solo puede asociarse a una `Categoria` de tipo `GASTO`.
- No puede haber dos presupuestos para la misma categoría, mes y año.
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
- Frontend: servicios en `src/api/` por recurso (hablan con `apiClient`),
  store de Pinia en `src/store/`, layouts en `src/layouts/`, vistas en
  `src/views/`, componentes reutilizables en `src/components/<dominio>/` o
  `src/components/common/` si son genéricos.
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
  (no es un servicio del sistema). El rol `finanzas_user` tiene `CREATEDB`
  para que `manage.py test` pueda crear la base de test.
- El repositorio vive en `~/Projects/finanzas-personales` (se movió fuera de
  `~/Desktop` en la Etapa 0 por un problema de permisos de macOS con las
  herramientas de vista previa).

Ver [README.md](README.md) para los pasos de instalación y ejecución.

## Uso de inteligencia artificial

Este proyecto se desarrolla con asistencia de Claude Code (Anthropic). El uso de
IA se documenta en `IA_USO.md`, como pide la cátedra ("es posible el uso, no
abuso, especificando las herramientas utilizadas").
