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

## API y frontend de Presupuestos (Etapa 5)

- El modelo `Presupuesto` ya existía desde la Etapa 1 — esta etapa solo
  agrega `serializers.py`, `views.py` y `urls.py` encima. Sin migraciones
  nuevas.
- **`gasto_real`, `porcentaje_utilizado` y `restante` son
  `SerializerMethodField`, calculados en cada serialización** con una query
  `Movimiento.objects.filter(...).aggregate(Sum("monto"))` (Decimal, nunca
  `float`), no se guardan en el modelo. Esto es justamente lo que hace que
  "se actualicen automáticamente cuando se crean, editan o eliminan
  movimientos": no hay nada que invalidar ni recalcular con señales, el
  valor siempre es fresco porque nunca se cachea en la base. El resultado sí
  se cachea por-instancia dentro del propio `PresupuestoSerializer`
  (`obj._gasto_real_cache`) para que los 3 campos de una misma fila no
  disparen 3 queries idénticas.
- Mismo patrón de validación que `Categoria`/`Movimiento`: `categoria` no es
  restringible por queryset, se valida explícitamente en
  `PresupuestoSerializer.validate()` (pertenencia al usuario, tipo `GASTO`,
  unicidad por `usuario`+`categoria`+`mes`+`anio` excluyendo la instancia
  actual en updates) para poder dar un mensaje de error claro por campo.
- `PresupuestoViewSet.get_queryset()` acepta `?mes=&anio=` **opcionales**
  (a diferencia del dashboard, acá no son obligatorios: sin filtros, lista
  todos los presupuestos del usuario en cualquier período).
- **`apps/dashboard/presupuestos_resumen`** es un endpoint nuevo, separado
  de `resumen`: suma `monto_limite` de los presupuestos del período y el
  gasto real **solo** de esas categorías (`categoria_id__in=...`), nunca el
  gasto general. No hay riesgo de contar un gasto dos veces porque
  `Presupuesto` es único por categoría+período, así que `categoria_ids` no
  tiene duplicados.
- **Frontend — umbrales de color compartidos:** `claseUtilizacion()` en
  `utils/format.js` centraliza los 3 estados (`<80%` verde, `80-99%`
  amarillo, `≥100%` rojo) para que el mini-resumen del Dashboard y la vista
  de Presupuestos usen exactamente el mismo criterio.
- **Frontend — "Excedido en" en vez de restante negativo:** `PresupuestoCard`
  muestra `Math.abs(restante)` con la etiqueta "Excedido en" cuando es
  negativo, en vez de mostrar directamente `-$5.000,00` (menos confuso para
  el usuario).
- `MESES` y `aniosDisponibles()` se movieron de `DashboardView.vue` a
  `utils/format.js` en esta etapa para que `PresupuestoFormModal` y
  `PresupuestosView` los reusaran sin duplicar el array.

## API y frontend de Evolución mensual (Etapa 6)

- `apps/dashboard/evolucion_mensual` agrupa con
  `.values("fecha__month", "categoria__tipo").annotate(total=Sum("monto"))`
  sobre `Movimiento` filtrado por usuario y año — una sola query, sin
  N+1 por mes. El resultado se vuelca a dos diccionarios (`ingresos_por_mes`,
  `gastos_por_mes`) pre-poblados con `Decimal("0.00")` para los 12 meses, así
  que un mes sin movimientos no requiere lógica especial: ya está en cero.
- `validators.py` se refactorizó: `_validar_anio()` es el helper compartido
  entre `parse_periodo` (mes + año, usado por `resumen` /
  `gastos_por_categoria` / `presupuestos_resumen`) y el nuevo `parse_anio`
  (solo año, usado acá) — mismo criterio de validación sin duplicar código.
- **Frontend — segundo gráfico, mismo patrón que la dona:** `DashboardView`
  ahora maneja dos instancias de Chart.js (`chartInstance` para la dona,
  `evolucionChartInstance` para las barras agrupadas), cada una con su propio
  par destruir/crear. `cargarDashboard()` dispara los 4 endpoints del
  dashboard en paralelo (`Promise.all`) y después resuelve los dos gráficos
  en secuencia. El gráfico de evolución técnicamente solo depende de `anio`
  (no de `mes`), pero se recarga con el mismo handler unificado por
  simplicidad — el costo de una llamada HTTP de más al cambiar el mes es
  insignificante comparado con mantener dos flujos de carga separados.
- **Frontend — Chart.js: se agregaron los registrables de barras**
  (`BarController`, `BarElement`, `CategoryScale`, `LinearScale`) a los que
  ya estaban registrados para la dona (`ArcElement`, `DoughnutController`).
  Mismo criterio de la Etapa 4: solo se registra lo que se usa, sin importar
  `chart.js/auto`.
- `MESES_CORTOS` (abreviaturas de 3 letras) se agregó a `utils/format.js`
  para el eje X del gráfico de barras — Chart.js además recorta
  automáticamente las etiquetas visibles en pantallas angostas (se ve en el
  QA mobile: se muestran Ene/Mar/May/Jul/Sep/Nov salteando de a uno).
- El eje Y del gráfico de barras formatea los ticks a mano
  (`"$ " + value.toLocaleString('es-AR')`, sin decimales) en vez de
  reusar `formatMonto` tal cual — mostrar centavos en cada línea de grilla
  es ruido visual innecesario; los tooltips sí usan `formatMonto` completo.

## Correcciones de calidad y seguridad (Etapa 7A.1)

Tras la auditoría de la Etapa 7A, se corrigieron los hallazgos confirmados
(sin tocar JWT, arquitectura ni funcionalidades — eso quedó fuera de
alcance a propósito):

- **`DEBUG` seguro por defecto:** `config/settings.py` ahora usa
  `_env_bool("DJANGO_DEBUG", "False")` — si falta la variable, arranca en
  `False`. `backend/.env`/`.env.example` siguen fijando
  `DJANGO_DEBUG=True` explícitamente para desarrollo, así que el entorno
  local no cambió de comportamiento. Cubierto por
  `apps/core/tests.py::SettingsSeguraPorDefectoTests`: dos tests unitarios
  sobre `_env_bool` (el helper que de verdad calcula el valor — no se
  recarga todo el módulo de settings dentro del test, sería mucho más
  frágil) y un test "guarda de regresión" que lee el código fuente de
  `settings.py` y falla si alguien vuelve a poner `"True"` como default.
- **Condición de carrera en selectores de período:** `DashboardView.vue` y
  `PresupuestosView.vue` ahora llevan un contador `requestId` que se
  incrementa en cada llamada a `cargarDashboard()`/`cargarPresupuestos()`;
  cada punto de la función que toca estado compartido (refs, gráficos)
  chequea primero que su `requestId` siga siendo el vigente, si no, corta
  sin tocar nada. Se probó disparando 4 combinaciones de mes/año seguidas
  sin esperar cada respuesta — el estado final siempre quedó consistente
  con el último período seleccionado. No se usó `AbortController` porque
  hubiera requerido pasar un `signal` a través de todo `api/*.js`; el
  contador de request logra lo mismo tocando solo las dos vistas.
- **Accesibilidad de teclado en modales:** los 4 modales custom
  (`ConfirmDialog`, `CategoriaFormModal`, `MovimientoFormModal`,
  `PresupuestoFormModal`) ahora usan un composable nuevo,
  `src/composables/useModalA11y.js` — no es una librería externa, es una
  función de Vue plano — que da Escape-para-cerrar, foco inicial dentro
  del modal al abrir, trampa de Tab/Shift+Tab, y restauración del foco al
  elemento que lo abrió al cerrar. Se centralizó en un composable en vez
  de un `BaseModal.vue` para no tocar el markup/CSS de cada modal (fuera
  de alcance de esta etapa) — cada componente solo agrega 5 líneas de
  `<script setup>` y un `ref="modalRef"` en su contenedor.
  - Verificado con eventos de teclado reales (`KeyboardEvent` con
    `key: 'Tab'`/`'Escape'`), no solo leyendo el código: Tab desde el
    último campo vuelve al primero, Shift+Tab desde el primero vuelve al
    último, Escape cierra y restaura el foco — confirmado en
    `PresupuestoFormModal` y `CategoriaFormModal`.
  - Nota de QA: un `.click()` disparado por JavaScript (como los que usa
    este proyecto para probar la UI vía herramientas de automatización) no
    mueve el foco del navegador de la misma forma que un click real — por
    eso la restauración de foco "falló" en una primera prueba hasta
    enfocar el botón a mano antes de abrir el modal. Es una particularidad
    del entorno de pruebas, no un bug: con interacción real (mouse o
    teclado) el navegador sí foca el botón al hacer click, y la
    restauración funciona.
- **Labels de filtros:** `MovimientosView.vue` (Desde/Hasta/Tipo/Categoría)
  ahora usa `id`+`for` igual que los formularios modales;
  `PresupuestosView.vue` (selects de mes/año) ahora usa `aria-label`, igual
  que `DashboardView.vue`.
- **Cobertura de tests para `PATCH` inválido:** se agregaron tests que
  confirman que un `PATCH` con monto negativo, categoría ajena, límite de
  presupuesto inválido o categoría de ingreso en un presupuesto son
  rechazados con `400` **y que el registro en la base queda exactamente
  igual que antes del intento** (`refresh_from_db()` + `assertEqual` contra
  el valor original) — no alcanza con que el endpoint rechace la request,
  hay que confirmar que no mutó nada a medias.

## Documentación técnica y manual de usuario (Etapa 7B)

Se agregó `docs/` con tres documentos verificados contra el código real
(no contra el diseño original): `DOCUMENTACION_TECNICA.md` (arquitectura,
modelo de datos, endpoints, reglas de negocio, cálculos, seguridad,
limitaciones conocidas), `MANUAL_USUARIO.md` (guía de uso sin
conocimientos de programación) y `DIAGRAMAS.md` (4 diagramas Mermaid:
arquitectura general, entidad-relación, flujo de autenticación, flujo de
registro de un movimiento y actualización del dashboard). El README y
este archivo se dejaron como están en cuanto a contenido técnico — solo
se agregó un enlace a `docs/` — para no mantener la misma información
duplicada en dos lugares.

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
  ingresos/gastos/balance y gráfico de gastos por categoría. ✅ completo
  (Etapas 0-4).
- **Iteración 2:** presupuestos mensuales con % utilizado ✅ (Etapa 5),
  gráfico de evolución mensual ✅ (Etapa 6). ✅ completa.
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
