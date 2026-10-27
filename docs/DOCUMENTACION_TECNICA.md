# Documentación técnica

Sistema Web de Gestión de Finanzas Personales — Tecnicatura en Programación de
Computadoras, Universidad de Belgrano. Alumno: Axel Flores. Docente tutor:
Mg. Ing. Guillermo Ramiro Maquieira. Fecha de presentación: 26/11/2026.

Este documento describe el sistema **tal como está implementado** en el
repositorio al commit `93bc57a` (Etapa 7A.1). Cada sección fue verificada
contra el código real (modelos, serializers, vistas, rutas, componentes) y
no contra el diseño original; donde el diseño cambió durante el desarrollo,
se documenta lo que efectivamente quedó funcionando.

## 1. Introducción y objetivo del proyecto

El proyecto es una aplicación web de finanzas personales que permite a un
usuario registrar sus ingresos y gastos, organizarlos por categorías,
definir presupuestos mensuales por categoría de gasto, y visualizar su
situación financiera en un dashboard con gráficos.

Objetivo académico: aplicar en un caso real los contenidos de la materia
Prácticas de Laboratorio — diseño de un modelo de datos relacional,
construcción de una API REST autenticada, consumo de esa API desde una
interfaz Vue, y un ciclo de trabajo iterativo con control de versiones.

## 2. Problema que resuelve

Una persona que quiere llevar el control de sus finanzas personales
necesita, como mínimo: un lugar donde registrar cada movimiento de dinero
(sin depender de una planilla manual propensa a errores de fórmulas),
una forma de agruparlos por tipo de gasto/ingreso para entender en qué se
va la plata, un límite de gasto por categoría que avise cuando se está
cerca de superarlo, y una vista resumida que no obligue a sumar columnas a
mano. El sistema cubre esas cuatro necesidades para un único usuario por
instalación (no es una app multi-tenant con registro público).

## 3. Alcance y funcionalidades implementadas

Implementado y en producción en el repositorio:

- Autenticación JWT (login, refresh, perfil del usuario autenticado).
- CRUD completo de categorías, tipadas `INGRESO` o `GASTO`.
- CRUD completo de movimientos (ingresos y gastos), con filtros por fecha,
  tipo y categoría.
- CRUD completo de presupuestos mensuales por categoría de gasto, con
  cálculo en vivo de gasto real, porcentaje utilizado y restante.
- Dashboard con resumen de ingresos/gastos/balance del período, gráfico de
  gastos por categoría (dona), gráfico de evolución mensual ingresos vs.
  gastos (barras), y mini-resumen de presupuestos del período.
- Aislamiento estricto de datos entre usuarios (ver sección 15).

**No implementado / explícitamente fuera de alcance** (ver sección 18):
registro público de usuarios, multi-moneda, rotación/blacklist de refresh
tokens, exportación de datos, notificaciones.

## 4. Arquitectura general del sistema

Arquitectura de tres capas, backend y frontend desacoplados y servidos por
separado en desarrollo:

```
┌─────────────────────────┐        ┌──────────────────────────┐        ┌──────────────┐
│   Vue 3 SPA (Vite)      │  HTTPS/│  Django REST Framework    │  ORM   │  PostgreSQL  │
│   puerto 5173           │ ─────► │  puerto 8000              │ ─────► │  puerto 5432 │
│   Axios + JWT en Pinia  │ JSON   │  JWTAuthentication         │        │              │
└─────────────────────────┘        └──────────────────────────┘        └──────────────┘
```

- El frontend es una SPA que nunca renderiza HTML del lado del servidor:
  todo el contenido se arma en el navegador a partir de las respuestas JSON
  de la API.
- El backend no sirve ninguna vista HTML propia (salvo `/admin/` de
  Django): su única responsabilidad es la API REST bajo `/api/`.
- No hay caché intermedia, cola de tareas ni microservicios: es una
  aplicación monolítica simple, consistente con el alcance de un trabajo
  práctico de esta materia.

Ver diagrama Mermaid ampliado en [DIAGRAMAS.md](DIAGRAMAS.md#arquitectura-general).

## 5. Tecnologías utilizadas y justificación

| Tecnología | Uso | Por qué |
|---|---|---|
| Django 6.1 + Django REST Framework | API backend | Framework maduro con ORM, migraciones, admin y autenticación integrados; DRF da serialización, ViewSets y permisos sin reinventar nada de eso. |
| `djangorestframework-simplejwt` | Autenticación | JWT estándar, bien integrado con DRF, sin necesidad de sesiones de servidor con estado. |
| PostgreSQL | Base de datos | Soporta bien `DecimalField` (crítico para montos de dinero, nunca `float`) y constraints a nivel de base (`CheckConstraint`, `UniqueConstraint`). |
| Vue 3 (Composition API) + Vite | Frontend | Curva de aprendizaje razonable para el alcance del TP, `<script setup>` mantiene cada componente compacto, Vite da un dev server rápido. |
| Pinia | Estado global del frontend | Store oficial recomendado por el equipo de Vue 3, reemplaza a Vuex con una API más simple. |
| Bootstrap 5 (solo CSS) | Estilos | Clases listas para layout/formularios/alertas sin escribir CSS desde cero; se usa **sin su JS/Popper** porque los modales se controlan con `v-if` de Vue (ver sección 9 y `CLAUDE.md`). |
| Chart.js (sin wrapper) | Gráficos | Librería liviana y muy usada; se instancia directamente (`new Chart(...)`) en vez de `vue-chartjs` para controlar explícitamente el ciclo de vida (destroy/recreate) sin una capa de abstracción adicional. |
| Axios | Cliente HTTP | Interceptores de request/response nativos, necesarios para adjuntar el token y manejar el refresh automático ante un `401`. |

## 6. Estructura del repositorio

```
finanzas-personales/
├── backend/
│   ├── apps/
│   │   ├── core/          # health check, JWT endpoints, /auth/me/
│   │   ├── categorias/    # modelo, serializer, viewset, tests
│   │   ├── movimientos/   # modelo, serializer, viewset, tests
│   │   ├── presupuestos/  # modelo, serializer, viewset, tests
│   │   └── dashboard/     # vistas agregadas de solo lectura (sin modelos)
│   ├── config/            # settings.py, urls.py, wsgi/asgi
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api/           # clientes Axios por recurso (categorias.js, movimientos.js, ...)
│       ├── components/    # componentes reutilizables por dominio (categorias/, movimientos/, presupuestos/, common/)
│       ├── composables/   # useModalA11y.js
│       ├── layouts/       # AppLayout.vue (sidebar + router-view)
│       ├── router/        # index.js (rutas y guard de autenticación)
│       ├── store/         # auth.js (Pinia)
│       ├── utils/         # format.js (moneda, fechas, umbrales)
│       └── views/         # LoginView, DashboardView, CategoriasView, MovimientosView, PresupuestosView
├── docs/                  # este documento, manual de usuario y diagramas
├── README.md              # instalación y referencia de endpoints
├── CLAUDE.md               # decisiones técnicas y convenciones del proyecto
└── IA_USO.md               # registro de uso de IA por etapa
```

## 7. Modelo de datos

Tres entidades, todas con `usuario` como FK a `django.contrib.auth.User`
(modelo de usuario de Django sin personalizar) y aislamiento por usuario en
cada consulta.

### `Categoria` (`apps/categorias/models.py`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `usuario` | FK → User, `on_delete=CASCADE` | — |
| `nombre` | `CharField(100)` | — |
| `tipo` | `CharField` con choices | `INGRESO` o `GASTO` |
| `creado_en` | `DateTimeField` | `auto_now_add=True` |

Restricción: `UniqueConstraint(usuario, nombre, tipo)` — un mismo usuario no
puede tener dos categorías con el mismo nombre y tipo.

### `Movimiento` (`apps/movimientos/models.py`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `usuario` | FK → User, `CASCADE` | — |
| `categoria` | FK → Categoria, `PROTECT` | no se puede borrar una categoría con movimientos |
| `monto` | `DecimalField(12,2)` | `MinValueValidator(0.01)` + `CheckConstraint(monto > 0)` |
| `fecha` | `DateField` | — |
| `descripcion` | `CharField(255)` | opcional (`blank=True`) |
| `creado_en` / `actualizado_en` | `DateTimeField` | auto |

El campo `tipo` del movimiento **no existe en el modelo**: se deriva de
`categoria.tipo` (ver sección 12). `clean()` valida que la categoría
pertenezca al mismo usuario que el movimiento (defensa en profundidad,
repetida en el serializer).

### `Presupuesto` (`apps/presupuestos/models.py`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `usuario` | FK → User, `CASCADE` | — |
| `categoria` | FK → Categoria, `PROTECT` | debe ser tipo `GASTO` (validado en `clean()` y en el serializer) |
| `mes` | `PositiveSmallIntegerField` | 1-12 (`CheckConstraint` + validators) |
| `anio` | `PositiveSmallIntegerField` | ≥ 2000 |
| `monto_limite` | `DecimalField(12,2)` | > 0 |
| `creado_en` | `DateTimeField` | auto |

Restricción: `UniqueConstraint(usuario, categoria, mes, anio)` — un usuario
no puede tener dos presupuestos para la misma categoría en el mismo
mes/año.

### Relaciones

- `User 1 — N Categoria`
- `User 1 — N Movimiento`, `Categoria 1 — N Movimiento`
- `User 1 — N Presupuesto`, `Categoria 1 — N Presupuesto`

No hay tabla de moneda (todos los montos se asumen en ARS) ni tabla de
"usuario" propia: se usa el modelo `User` estándar de `django.contrib.auth`.

## 8. Diagrama entidad-relación

Ver [DIAGRAMAS.md](DIAGRAMAS.md#entidad-relación).

## 9. Arquitectura de comunicación frontend/backend

- El frontend llama a la API vía dos instancias de Axios
  (`frontend/src/api/axios.js` y `api/authClient.js`), ambas con
  `baseURL` tomado de `VITE_API_URL` (`.env` del frontend).
- **`authClient.js`**: sin interceptores. Lo usa únicamente el store de
  auth para login, refresh y `/auth/me/`. Se mantiene separado para evitar
  una dependencia circular (`axios.js` importa el store, que si usara
  `axios.js` para el refresh, importaría a `axios.js` de nuevo) y para que
  un refresh fallido no dispare otro refresh en bucle.
- **`axios.js`** (usado por `api/categorias.js`, `api/movimientos.js`,
  `api/presupuestos.js`, `api/dashboard.js`):
  - Interceptor de **request**: si hay `accessToken` en el store, agrega
    `Authorization: Bearer <token>`.
  - Interceptor de **response**: si una respuesta da `401` y la request no
    se reintentó todavía, intenta un refresh (una sola promesa compartida
    `refreshPromise` para no disparar refreshes en paralelo si varias
    requests fallan a la vez), reintenta la request original con el token
    nuevo, y si el refresh también falla, desloguea y redirige a
    `/login?expired=1`.
- Cada recurso del frontend tiene su propio módulo en `src/api/` que expone
  funciones simples (`listCategorias()`, `createMovimiento(payload)`, etc.)
  que llaman a `axios.js` — las vistas nunca importan Axios directamente.
- El router (`src/router/index.js`) tiene un guard global
  (`router.beforeEach`) que redirige a `/login` si la ruta no es pública y
  no hay sesión activa (`authStore.isAuthenticated`), y redirige a
  `/dashboard` si se intenta visitar `/login` ya autenticado.

## 10. Autenticación JWT y autorización

- Librería: `djangorestframework-simplejwt`. Configuración real
  (`backend/config/settings.py`):
  - `DEFAULT_AUTHENTICATION_CLASSES = ["rest_framework_simplejwt.authentication.JWTAuthentication"]`
  - `DEFAULT_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]` (por defecto en **todos** los endpoints salvo que se anule explícitamente).
  - `ACCESS_TOKEN_LIFETIME = 1 hora`, `REFRESH_TOKEN_LIFETIME = 7 días`. Sin
    rotación de refresh tokens ni blacklist (decisión explícita, ver
    sección 18 — límite de alcance acordado para la Etapa 7A.1).
- Endpoints públicos (`AllowAny` o fuera del alcance de `IsAuthenticated`
  por diseño): `GET /api/health/`, `POST /api/auth/token/`,
  `POST /api/auth/token/refresh/`. Todo el resto exige
  `Authorization: Bearer <access_token>`.
- No hay registro público de usuarios: el único usuario de la app se crea
  con el comando de management `seed_test_user`, que lee
  `TEST_USER_USERNAME`/`TEST_USER_PASSWORD`/`TEST_USER_EMAIL` desde
  `backend/.env` (nunca se commitea una contraseña real).
- **Autorización** (quién puede ver/editar qué): no se basa en permisos de
  DRF por objeto, sino en que **cada `get_queryset()` de cada ViewSet
  filtra explícitamente por `usuario=request.user`** (`CategoriaViewSet`,
  `MovimientoViewSet`, `PresupuestoViewSet`). Acceder por id a un recurso
  de otro usuario no entra en el queryset, así que DRF devuelve `404` (no
  `403`): esto evita confirmarle a un atacante que el recurso existe.
- **Frontend**: el access y el refresh token viven **solo en memoria**
  (estado de la store de Pinia `useAuthStore`), nunca en `localStorage` ni
  `sessionStorage`. Decisión consciente: minimiza la superficie de robo de
  token ante un XSS, a costa de que recargar la página cierra la sesión
  (no hay nada que rehidratar).

## 11. Endpoints REST reales

Todos bajo el prefijo `/api/` (`backend/config/urls.py`). Los que no
figuran como `AllowAny` requieren `Authorization: Bearer <access>`.

### Autenticación (`apps/core`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/health/` | Público. `{"status": "ok", "database": "ok"}` o `"error"` si no hay conexión a la base. |
| `POST` | `/api/auth/token/` | Público. `{"username", "password"}` → `{"access", "refresh"}`. |
| `POST` | `/api/auth/token/refresh/` | Público. `{"refresh"}` → `{"access"}`. |
| `GET` | `/api/auth/me/` | Autenticado. `{"username", "email"}` del usuario del token. |

### Categorías (`apps/categorias`, `ModelViewSet` vía `DefaultRouter`)

| Método | Ruta | Body / notas |
|---|---|---|
| `GET` | `/api/categorias/` | Lista las del usuario autenticado. |
| `POST` | `/api/categorias/` | `{"nombre", "tipo": "INGRESO"\|"GASTO"}`. `400` si ya existe una con el mismo nombre+tipo para ese usuario. |
| `GET` | `/api/categorias/{id}/` | `404` si no existe o es de otro usuario. |
| `PATCH` | `/api/categorias/{id}/` | Mismas validaciones que el alta. |
| `DELETE` | `/api/categorias/{id}/` | `409 Conflict` si tiene movimientos o presupuestos asociados (`ProtectedError` capturado explícitamente). |

### Movimientos (`apps/movimientos`)

| Método | Ruta | Body / notas |
|---|---|---|
| `GET` | `/api/movimientos/?fecha_desde=&fecha_hasta=&tipo=&categoria=` | Filtros opcionales y combinables, todos validados a mano (ver sección 12). |
| `POST` | `/api/movimientos/` | `{"categoria": id, "monto": "1500.00", "fecha": "2026-10-15", "descripcion": "..."}`. `tipo` y `categoria_nombre` son read-only en la respuesta. |
| `GET` / `PATCH` / `DELETE` | `/api/movimientos/{id}/` | Scopeado al usuario; `404` si es ajeno. |

### Presupuestos (`apps/presupuestos`)

| Método | Ruta | Body / notas |
|---|---|---|
| `GET` | `/api/presupuestos/?mes=&anio=` | Filtros **opcionales** (a diferencia del dashboard). |
| `POST` | `/api/presupuestos/` | `{"categoria": id, "mes": 10, "anio": 2026, "monto_limite": "150000.00"}`. |
| `GET` / `PATCH` / `DELETE` | `/api/presupuestos/{id}/` | Respuesta incluye `gasto_real`, `porcentaje_utilizado`, `restante` calculados en vivo. |

### Dashboard (`apps/dashboard`, vistas de función, sin modelos propios)

| Método | Ruta | `mes`/`anio` |
|---|---|---|
| `GET` | `/api/dashboard/resumen/?mes=&anio=` | Obligatorios ambos. |
| `GET` | `/api/dashboard/gastos-por-categoria/?mes=&anio=` | Obligatorios ambos. |
| `GET` | `/api/dashboard/presupuestos-resumen/?mes=&anio=` | Obligatorios ambos. |
| `GET` | `/api/dashboard/evolucion-mensual/?anio=` | Solo `anio`, siempre devuelve los 12 meses. |

Ejemplos de request/response completos (con JSON real) para cada uno de
estos cuatro endpoints están en el [README.md](../README.md#dashboard), para
no duplicar el mismo contenido en dos archivos.

## 12. Reglas de negocio y validaciones

- Un usuario solo puede ver, editar o eliminar sus propios recursos
  (categorías, movimientos, presupuestos) — aplicado en `get_queryset()`
  de cada ViewSet, nunca confiando en lo que venga en el body.
- `usuario` **nunca es un campo del serializer**: en los tres recursos se
  asigna explícitamente en `create()` desde
  `self.context["request"].user`, así que no se puede suplantar a otro
  usuario mandando `usuario` en el body (DRF ni siquiera lo aceptaría como
  campo).
- La pertenencia de `categoria` al usuario se valida explícitamente en
  cada serializer (`validate()` o `validate_categoria()`), no solo con un
  queryset filtrado, porque `usuario` no es un campo visible del
  serializer y DRF no puede auto-validarlo.
- Montos (`Movimiento.monto`, `Presupuesto.monto_limite`): `DecimalField`
  con `MinValueValidator(0.01)` a nivel de modelo/serializer **y**
  `CheckConstraint` a nivel de base de datos — doble capa, uno para dar un
  mensaje de error claro en la API, otro como última defensa si algo
  escribiera directo contra la base.
- `Presupuesto.categoria` debe ser de tipo `GASTO` — validado en
  `clean()` del modelo y en `PresupuestoSerializer.validate()`.
- Unicidad: `Categoria` por (`usuario`, `nombre`, `tipo`); `Presupuesto`
  por (`usuario`, `categoria`, `mes`, `anio`) — ambas validadas
  explícitamente en el serializer (no con el `UniqueTogetherValidator`
  automático de DRF, porque `usuario` no es un campo del serializer) y
  reforzadas con `UniqueConstraint` en la base.
- Filtros de `MovimientoViewSet` (`fecha_desde`, `fecha_hasta`, `tipo`,
  `categoria`) se implementan a mano en `get_queryset()`, sin
  `django-filter`, para poder devolver mensajes de error específicos por
  campo ante un valor inválido en vez de ignorarlo silenciosamente. Caso
  particular: `django.utils.dateparse.parse_date` lanza `ValueError` (no
  devuelve `None`) ante una fecha sintácticamente válida pero imposible
  (`"2026-99-99"`); el código lo envuelve en `try/except` para devolver
  `400` en vez de un error 500.
- `categoria` como filtro de movimientos: si el id no es numérico, `400`;
  si es numérico pero no existe o es de otro usuario, lista vacía (no se
  revela si el recurso existe).
- Borrar una categoría con movimientos o presupuestos asociados
  (`on_delete=PROTECT`) devuelve `409 Conflict`, no `500` ni `400`.

## 13. Cálculos de ingresos, gastos, balances y presupuestos

- **Todo cálculo monetario usa `Decimal`, nunca `float`** (verificado por
  grep sobre todo el backend durante la auditoría de la Etapa 7A). Las
  respuestas serializan los montos como **string** (`"150000.00"`), no
  como número JSON, para eliminar cualquier ambigüedad de precisión del
  lado del cliente.
- `dashboard.resumen`: suma `monto` de los movimientos del usuario en el
  período filtrando por `categoria__tipo`, por separado para `INGRESO` y
  `GASTO`; `balance = ingresos - gastos`.
- `dashboard.gastos_por_categoria`: agrupa con
  `.values("categoria_id", "categoria__nombre").annotate(total=Sum("monto"))`
  sobre movimientos de tipo `GASTO`; el porcentaje de cada categoría se
  calcula sobre el total de gastos del período (`monto / total_gastos * 100`).
  Una categoría sin movimientos en el período no aparece en la lista (no
  se agrega con monto 0).
- `Presupuesto.gasto_real` / `porcentaje_utilizado` / `restante`
  (`PresupuestoSerializer`, `SerializerMethodField`): se calculan **en cada
  serialización**, nunca se guardan en el modelo. `gasto_real` es la suma
  (`Sum`) de los movimientos del usuario con esa `categoria` en ese
  `mes`/`anio`; `porcentaje_utilizado = gasto_real / monto_limite * 100`;
  `restante = monto_limite - gasto_real` (puede ser negativo si se superó
  el límite). El resultado se cachea por instancia
  (`obj._gasto_real_cache`) dentro del propio serializer para que los tres
  campos de una misma fila no disparen tres queries idénticas — no hay
  caché entre requests ni se persiste nada.
- `dashboard.presupuestos_resumen`: suma `monto_limite` de todos los
  presupuestos del período (`presupuesto_total`) y, por separado, el gasto
  real **solo** de las categorías que tienen presupuesto en ese período
  (`gasto_real_presupuestado`, vía `categoria_id__in=[...]`) — deliberadamente
  distinto del `gastos` general de `resumen`, para no mezclar "todo lo que
  gasté" con "lo que gasté en categorías presupuestadas".
- `dashboard.evolucion_mensual`: una sola query agrupada
  (`.values("fecha__month", "categoria__tipo").annotate(total=Sum("monto"))`)
  sobre todos los movimientos del año; el resultado se distribuye en dos
  diccionarios (`ingresos_por_mes`, `gastos_por_mes`) pre-poblados con
  `Decimal("0.00")` para los 12 meses, así que un mes sin movimientos queda
  en cero sin lógica especial.

## 14. Gráficos y agregaciones mensuales

- **Gráfico de dona (gastos por categoría)**: `DashboardView.vue`, Chart.js
  tipo `doughnut`, alimentado por `dashboard.gastos_por_categoria`. Una
  paleta fija de 8 colores (`PALETA` en el componente) se asigna por
  índice; con más de 8 categorías los colores se repiten.
- **Gráfico de barras agrupadas (evolución mensual)**: tipo `bar`, dos
  datasets (`Ingresos` verde, `Gastos` rojo), alimentado por
  `dashboard.evolucion_mensual`. Eje X con las 12 abreviaturas de mes
  (`MESES_CORTOS`); eje Y formateado a mano como pesos sin centavos
  (`"$ " + value.toLocaleString('es-AR')`) para no ensuciar la grilla, los
  tooltips sí muestran el monto completo con `formatMonto()`.
- Ambos gráficos se instancian con `new Chart(canvasRef.value, {...})`
  directamente (sin `vue-chartjs`) y se destruyen explícitamente
  (`chartInstance.destroy()`) antes de cada recreación y en
  `onBeforeUnmount`, para evitar el error "Canvas is already in use" de
  Chart.js cuando el `v-if` del estado vacío desmonta el `<canvas>`.
- `Chart.register(...)` solo registra los componentes realmente usados
  (`ArcElement`, `DoughnutController`, `BarController`, `BarElement`,
  `CategoryScale`, `LinearScale`, `Tooltip`, `Legend`) — no se importa
  `chart.js/auto`.
- Protección contra condición de carrera: `cargarDashboard()` usa un
  contador `dashboardRequestId` module-scoped. Cada llamada toma un id al
  empezar; después de cada `await` (las cuatro peticiones en paralelo y
  cada `nextTick()` antes de crear un gráfico) se verifica que el id siga
  siendo el vigente, y si no, se corta sin tocar estado ni gráficos. Esto
  evita que, ante cambios rápidos de mes/año, una respuesta vieja que
  llega tarde pise el estado de una más reciente (mismo patrón en
  `PresupuestosView.vue` con `presupuestosRequestId`).

## 15. Seguridad y aislamiento entre usuarios

Verificado durante la auditoría de la Etapa 7A (evidencia real, no
hipotética) y mantenido en la Etapa 7A.1:

- Cada `ViewSet` filtra su `get_queryset()` por `usuario=request.user`;
  acceder a un recurso de otro usuario por id da `404`.
- `usuario` nunca es un campo de los serializers: no se puede suplantar a
  otro usuario vía el body de la request.
- CORS restringido a los orígenes de desarrollo autorizados
  (`CORS_ALLOWED_ORIGINS` en `backend/.env`), no `"*"`.
- `DJANGO_DEBUG` arranca en `False` si la variable no está definida
  (`_env_bool("DJANGO_DEBUG", "False")`, corregido en la Etapa 7A.1 — antes
  el default era `True`); en desarrollo local, `backend/.env` lo fija en
  `True` explícitamente.
- Sin credenciales en el repositorio: se verificó con grep sobre todo el
  historial de Git (no solo el working tree) que no hay contraseñas,
  secretos ni tokens reales commiteados; cada `.env` tiene su
  `.env.example` con placeholders.
- Tokens JWT solo en memoria del lado del frontend (nunca en
  `localStorage`/`sessionStorage`), reduciendo la superficie de robo vía
  XSS.
- **Limitación conocida, documentada y fuera de alcance de esta etapa**:
  los refresh tokens no tienen rotación ni blacklist — un refresh token
  sigue siendo válido durante sus 7 días aunque se emita uno nuevo. Ver
  sección 18.

## 16. Estrategia de pruebas y cobertura funcional

- **124 tests automatizados** (`python manage.py test`), todos backend,
  usando el test runner de Django (`TestCase`/`APITestCase` de DRF) contra
  una base de datos de test real (no mocks de la base).
- Organización: cada app tiene su propio módulo de tests
  (`apps/<app>/tests/test_api.py` o `tests.py`), cubriendo modelos
  (constraints, `clean()`) y endpoints (alta, edición, borrado, filtros,
  aislamiento entre usuarios, casos 400/404/409).
- Cobertura explícita de casos negativos que podrían pasar inadvertidos:
  `PATCH` con monto negativo, con categoría ajena, con límite de
  presupuesto inválido o negativo, con categoría de tipo `INGRESO` en un
  presupuesto — cada uno de estos tests no solo verifica el `400`, sino
  que hace `refresh_from_db()` y confirma que el registro en la base
  **no cambió** (agregados en la Etapa 7A.1, ver `CLAUDE.md`).
- Verificación manual en navegador real (no automatizada) en cada etapa:
  flujos completos de login, CRUD de cada recurso, estados vacíos/error,
  responsive mobile, consola del navegador sin errores, y en la Etapa
  7A.1 específicamente: condición de carrera (cambios rápidos de
  mes/año sin esperar cada respuesta) y accesibilidad de teclado con
  eventos de teclado reales (`Tab`, `Shift+Tab`, `Escape`).
- No hay tests automatizados de frontend (ni unitarios ni end-to-end): la
  verificación del frontend es manual en cada etapa, documentada en
  `IA_USO.md`. Ver sección 18.

## 17. Instalación y ejecución local

Los pasos completos de instalación (incluyendo el caso real de esta
máquina, sin permisos de administrador, vía `nvm` y Miniforge/conda-forge),
las variables de entorno necesarias y la verificación de que cada parte
levantó bien están en el [README.md](../README.md) — no se duplican acá
para no tener dos fuentes de verdad desactualizándose por separado.

## 18. Limitaciones conocidas y posibles mejoras futuras

Limitaciones aceptadas conscientemente, documentadas desde la auditoría de
la Etapa 7A y no resueltas por quedar fuera del alcance acordado para la
Etapa 7A.1:

- **Refresh tokens sin rotación ni blacklist**: un refresh token robado
  sigue siendo válido hasta su expiración (7 días), aunque se haya usado
  para emitir un nuevo access token. Mejora futura: rotación de refresh
  tokens (`ROTATE_REFRESH_TOKENS`) + blacklist de tokens usados.
- **Código duplicado en el frontend**: la función `extractErrorMessage` y
  el patrón de `showFeedback` (alerta temporal) están repetidos
  literalmente en `MovimientosView.vue` y `PresupuestosView.vue`; el CSS
  del backdrop de modal también se repite en los 4 componentes modal.
  Severidad baja (cosmético/mantenibilidad, sin impacto funcional).
  Mejora futura: extraer a un composable (`useFeedback`) y a una clase CSS
  global.
- **Sin registro público de usuarios**: el único usuario de la app se crea
  por línea de comandos (`seed_test_user`). Aceptable para el alcance de
  este TP (una sola persona usando su propia instancia).
- **Sesión no persistente**: recargar la página cierra la sesión (tokens
  solo en memoria). Decisión consciente de seguridad, no un bug.
- **Sin multi-moneda**: todos los montos se asumen en ARS. Si se
  necesitara soportar otra moneda, se agregaría un campo `moneda` al
  modelo sin romper lo existente.
- **Sin tests automatizados de frontend**: toda la verificación de UI es
  manual, repetida en cada etapa. Mejora futura: tests de componentes con
  Vitest + Vue Test Utils para los flujos más críticos (login, alta de
  movimiento).
- **`Etapa 7 — Cierre y documentación final`** (ver checklist del
  README): la documentación técnica y el manual de usuario se completan en
  esta misma etapa (7B); queda pendiente, si la cátedra lo requiere, un
  cierre adicional (por ejemplo una presentación o defensa) fuera del
  alcance de este documento.
