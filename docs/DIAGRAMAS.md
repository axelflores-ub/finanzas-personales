# Diagramas

Diagramas Mermaid del sistema, verificados contra la implementación real
(modelos, endpoints y componentes del repositorio al commit `93bc57a`).
Complementa a [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md).

## Arquitectura general

```mermaid
flowchart LR
    subgraph Cliente["Navegador"]
        SPA["Vue 3 SPA (Vite, :5173)\nPinia + Axios + Chart.js"]
    end

    subgraph Servidor["Servidor backend"]
        API["Django REST Framework (:8000)\nJWTAuthentication + IsAuthenticated"]
    end

    subgraph Datos["Base de datos"]
        DB[("PostgreSQL (:5432)")]
    end

    SPA -- "JSON sobre HTTP\nAuthorization: Bearer <access>" --> API
    API -- "ORM (consultas Sum/Decimal)" --> DB
    DB -. "filas" .-> API
    API -. "JSON" .-> SPA
```

## Entidad-relación

```mermaid
erDiagram
    USER ||--o{ CATEGORIA : "posee"
    USER ||--o{ MOVIMIENTO : "posee"
    USER ||--o{ PRESUPUESTO : "posee"
    CATEGORIA ||--o{ MOVIMIENTO : "clasifica"
    CATEGORIA ||--o{ PRESUPUESTO : "limita"

    USER {
        int id
        string username
        string email
    }
    CATEGORIA {
        int id
        int usuario_id FK
        string nombre
        string tipo "INGRESO o GASTO"
        datetime creado_en
    }
    MOVIMIENTO {
        int id
        int usuario_id FK
        int categoria_id FK
        decimal monto "> 0"
        date fecha
        string descripcion
        datetime creado_en
        datetime actualizado_en
    }
    PRESUPUESTO {
        int id
        int usuario_id FK
        int categoria_id FK "debe ser tipo GASTO"
        int mes "1-12"
        int anio "mayor o igual a 2000"
        decimal monto_limite "> 0"
        datetime creado_en
    }
```

Restricciones de unicidad (no representables en el diagrama ER estándar):
`CATEGORIA` única por (`usuario`, `nombre`, `tipo`); `PRESUPUESTO` único
por (`usuario`, `categoria`, `mes`, `anio`).

## Flujo de autenticación

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as Vue SPA
    participant S as Store (Pinia)
    participant A as API Django

    U->>F: Ingresa usuario y contraseña
    F->>S: login(username, password)
    S->>A: POST /api/auth/token/
    alt Credenciales válidas
        A-->>S: 200 { access, refresh }
        S->>S: Guarda access/refresh en memoria
        S->>A: GET /api/auth/me/ (Bearer access)
        A-->>S: 200 { username, email }
        S-->>F: Sesión activa
        F->>U: Redirige a /dashboard
    else Credenciales inválidas
        A-->>S: 401
        S-->>F: Error de login
        F->>U: Muestra mensaje de error
    end

    Note over F,A: En cada request posterior a un recurso protegido:
    F->>A: GET /api/<recurso>/ (Bearer access)
    alt Token vigente
        A-->>F: 200 datos
    else Token vencido (401)
        F->>S: refreshAccessToken()
        S->>A: POST /api/auth/token/refresh/ { refresh }
        alt Refresh válido
            A-->>S: 200 { access nuevo }
            F->>A: Reintenta request original (Bearer access nuevo)
            A-->>F: 200 datos
        else Refresh inválido o vencido
            A-->>S: 401
            S->>S: logout() — limpia tokens
            F->>U: Redirige a /login?expired=1
        end
    end
```

## Flujo de registro de un movimiento y actualización del dashboard

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as MovimientoFormModal.vue
    participant V as MovimientosView.vue
    participant A as API Django
    participant D as PostgreSQL
    participant DB as DashboardView.vue

    U->>F: Completa categoría, monto, fecha y confirma
    F->>V: emit("submit", payload)
    V->>A: POST /api/movimientos/ (Bearer access)
    A->>A: Valida: categoria del usuario, monto > 0
    alt Datos válidos
        A->>D: INSERT movimiento
        D-->>A: OK
        A-->>V: 201 Created
        V->>V: Cierra el modal, muestra feedback de éxito
        V->>A: GET /api/movimientos/ (recarga la lista)
        A-->>V: 200 lista actualizada
    else Datos inválidos (ej. monto <= 0, categoría ajena)
        A-->>V: 400 { campo: "mensaje" }
        V->>F: Muestra error en el formulario
        F->>U: El modal permanece abierto, nada se guardó
    end

    Note over DB,A: La próxima vez que el usuario visita o refresca el Dashboard:
    U->>DB: Entra a /dashboard (o cambia mes/año)
    DB->>A: GET /dashboard/resumen/, /gastos-por-categoria/,<br/>/presupuestos-resumen/ (Promise.all), /evolucion-mensual/
    A->>D: Sum(monto) agrupado por tipo/categoría/mes
    D-->>A: Totales recalculados (incluye el movimiento nuevo)
    A-->>DB: 200 JSON con montos actualizados
    DB->>DB: Destruye y recrea los gráficos Chart.js
    DB->>U: Muestra el resumen actualizado
```
