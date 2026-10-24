# Uso de Inteligencia Artificial

Como pide la cátedra, se documenta acá el uso de IA en el desarrollo de este
proyecto.

## Herramienta

- **Claude Code** (Anthropic), asistente de desarrollo basado en modelos Claude,
  usado como copiloto a lo largo de todo el proyecto.

## Cómo se usa

- Diseño de arquitectura, modelo de datos y plan de implementación, discutidos y
  aprobados por el alumno antes de implementarse (ver historial de commits y
  `CLAUDE.md`).
- Generación de código de backend (Django/DRF) y frontend (Vue 3) a partir de
  especificaciones revisadas por el alumno, etapa por etapa.
- Configuración de entorno de desarrollo (Node.js, PostgreSQL, variables de
  entorno) y verificación de que cada etapa funciona antes de avanzar.

## Qué NO hace la IA

- No decide el alcance ni las reglas de negocio del sistema: estos quedan
  definidos por el alumno y la propuesta de trabajo aprobada por la cátedra.
- No avanza de etapa sin confirmación explícita del alumno.

## Registro por etapa

| Etapa | Fecha | Resumen de uso de IA |
|---|---|---|
| 0 — Setup | 21/10/2026 | Instalación de entorno (Node vía nvm, PostgreSQL vía conda-forge por falta de permisos de administrador), scaffolding de Django+DRF y Vue+Vite, configuración de CORS y variables de entorno, endpoint `/api/health/` de verificación. |
| 1 — Modelo de datos y autenticación | 21/10/2026 | Modelos `Categoria`/`Movimiento`/`Presupuesto` con restricciones (unicidad, montos positivos, `PROTECT`), migraciones, registro en Django Admin, autenticación JWT (`djangorestframework-simplejwt`), comando `seed_test_user`, y 19 pruebas automatizadas de modelos y autenticación. |
| 2 — CRUD de categorías e interfaz Vue | 21/10/2026 | `CategoriaViewSet` + `CategoriaSerializer` (scoping por usuario, validación de duplicados, `409` al borrar en uso) y 14 tests de API nuevos (33 en total). Frontend: store de auth en Pinia (sesión solo en memoria), interceptores Axios (adjuntar token, refrescar en `401`, logout en sesión vencida), router con rutas protegidas, layout con sidebar, login, y CRUD completo de categorías (tabla, modal de alta/edición, confirmación de borrado, estados de carga/vacío/error). Verificado manualmente en el navegador: login, alta, edición, borrado, borrado bloqueado por relaciones, duplicado rechazado, sesión vencida, logout, y vista mobile. |
| 3 — CRUD de movimientos financieros | 21/10/2026 | `MovimientoViewSet` + `MovimientoSerializer` (tipo/categoría derivados, filtros por fecha/tipo/categoría implementados a mano para controlar los mensajes de error en vez de usar `django-filter`) y 27 tests de API nuevos (60 en total). Frontend: vista `/movimientos` con tabla, formulario con selector de categoría dependiente del tipo, filtros combinables, formato de moneda argentino (`$ 25.000,00`). Durante la verificación manual en el navegador se encontró y corrigió un bug real: el formulario de alta no inicializaba la categoría por defecto la primera vez que se abría (quedaba en blanco aunque se viera seleccionada en pantalla), causando un 400 al guardar sin tocar nada — documentado en `CLAUDE.md`. |
| 4 — Dashboard financiero MVP | 21/10/2026 | App `dashboard` sin modelos: `resumen` y `gastos-por-categoria`, agregados con `Sum` del ORM sobre `Movimiento`, validación de `mes`/`anio` compartida, todo en `Decimal` (sin `float` en ningún cálculo ni en la respuesta). 18 tests de API nuevos (78 en total). Frontend: `DashboardView` con KPIs (ingresos/gastos/balance con formato ARS y color), gráfico de dona con Chart.js (sin wrapper, con destroy/recreate manual en cada cambio de período y en `onBeforeUnmount`), selector de mes/año, estado vacío, y Dashboard como pantalla por defecto tras el login. Verificado en el navegador contra datos reales de PostgreSQL de etapas anteriores, incluyendo cambios rápidos de período para confirmar que el gráfico se destruye/recrea sin errores de consola. |
| 5 — Presupuestos mensuales | 24/10/2026 | `PresupuestoSerializer`/`ViewSet` sobre el modelo ya existente desde la Etapa 1 (sin migraciones nuevas): `gasto_real`/`porcentaje_utilizado`/`restante` calculados en vivo con `Sum`/`Decimal` en cada request (nunca almacenados, así se actualizan solos ante altas/bajas/ediciones de movimientos). Nuevo endpoint `dashboard/presupuestos-resumen/` separado del `resumen` general para no contar gastos dos veces. 27 tests de API nuevos en `presupuestos` + 6 en `dashboard` (105 en total). Frontend: vista `/presupuestos` con tarjetas totales, barra de progreso por categoría con 3 umbrales de color (verde/amarillo/rojo) compartidos con la mini-sección nueva del Dashboard, formulario con categorías filtradas a tipo GASTO, confirmación de borrado. Verificado en el navegador: alta, edición, borrado, duplicado rechazado, estado "superado" (>100%, rojo, "Excedido en $X"), estado de advertencia (80-99%, amarillo), y los totales contrastados directamente contra PostgreSQL con `psql`. |
