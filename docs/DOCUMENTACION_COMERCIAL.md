# Documentación comercial

Caso de negocio del Sistema de Gestión de Finanzas Personales — Tecnicatura
en Programación de Computadoras, Universidad de Belgrano. Alumno: Axel
Flores.

Este documento presenta el proyecto desde la perspectiva de producto, no
de implementación técnica (para eso está
[DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)): qué problema
resuelve, para quién, y por qué alguien lo elegiría. Todo lo que describe
corresponde a funcionalidad real, implementada y verificada en el
repositorio — no hay proyecciones de uso, cifras de mercado ni promesas
sobre funciones que no existen todavía.

## 1. El problema

Llevar el control de las finanzas personales día a día es, para la
mayoría de la gente, una de estas tres cosas:

- **No se hace.** Se gasta sin un registro real, y recién a fin de mes
  (o nunca) se entiende en qué se fue la plata.
- **Se hace en una planilla de cálculo**, que funciona al principio pero
  se vuelve tediosa de mantener: hay que armar las fórmulas a mano, no
  avisa cuando te estás por pasar de un límite que te pusiste, y un
  gráfico actualizado requiere acordarse de refrescarlo.
- **Se delega en una app bancaria o de terceros**, que suele mezclar el
  registro de gastos con publicidad, venta de productos financieros, o
  directamente no permite categorizar los movimientos como uno necesita.

El punto en común: ninguna de las tres opciones da, con poco esfuerzo,
una respuesta clara a la pregunta "¿cómo vengo este mes, y me estoy
pasando de lo que me propuse gastar en algo puntual?".

## 2. La solución

Una aplicación web simple, de un solo propósito: registrar ingresos y
gastos, clasificarlos por categoría, ponerse límites mensuales de gasto
por categoría, y ver todo resumido sin tener que calcular nada a mano.

Sin fricción innecesaria: no pide tarjeta de crédito, no vincula cuentas
bancarias (todo se carga a mano, lo que también evita darle acceso a los
movimientos reales de la cuenta a un tercero), no tiene publicidad ni
venta cruzada de productos financieros.

## 3. Público objetivo

- **Personas que ya intentaron llevar sus finanzas en una planilla** y
  abandonaron por la fricción de mantenerla, pero igual quieren control
  manual (no delegar en un banco o en una app de terceros con acceso a
  su cuenta).
- **Alguien con un objetivo de ahorro o gasto concreto** (por ejemplo,
  "no gastar más de $X en delivery este mes"), para quien la función de
  presupuestos por categoría es el motivo principal de uso.
- Explícitamente **no** apunta, en su estado actual, a quien necesita
  gestión financiera de un negocio, múltiples cuentas o monedas, ni a
  quien prefiere una sincronización automática con el banco.

## 4. Propuesta de valor

| Lo que ofrece | Por qué importa |
|---|---|
| Carga manual de movimientos, categorizados | Entender en qué se gasta, no solo cuánto. |
| Presupuestos mensuales por categoría, con alerta visual (verde/amarillo/rojo) | Saber que te estás por pasar de un límite *antes* de pasarte, no a fin de mes. |
| Dashboard con balance y gráficos del período | Una respuesta visual inmediata a "¿cómo vengo?", sin abrir una planilla. |
| Sin vincular cuentas bancarias ni tarjetas | Cero datos financieros sensibles en manos de un tercero — todo lo que sabe la app es lo que el usuario decide cargar. |
| Sin publicidad ni venta de productos financieros | El incentivo del producto es que el usuario entienda sus finanzas, no que contrate un préstamo o una tarjeta. |

## 5. Diferenciales frente a las alternativas actuales

- **Frente a una planilla de cálculo**: no hay fórmulas que armar ni
  mantener; los presupuestos y el dashboard se recalculan solos cada vez
  que se carga un movimiento nuevo.
- **Frente a una app bancaria o "fintech" con seguimiento de gastos**: no
  requiere vincular ninguna cuenta real, no tiene publicidad, y el
  usuario es dueño completo de qué carga y cómo lo categoriza (una
  app bancaria generalmente categoriza automático y a veces mal).
- **Frente a no llevar ningún registro**: el costo de entrada es bajo —
  cargar un movimiento lleva unos segundos, y el valor (saber si te estás
  por pasar de un presupuesto) se ve desde el primer mes de uso.

## 6. Estado actual y lo que falta para ser un producto

Siendo honestos sobre dónde está el proyecto hoy, para que la evaluación
sea realista:

- **Completo y funcional**: el producto principal (categorías,
  movimientos, presupuestos, dashboard) está terminado, probado (124
  tests automatizados) y auditado en seguridad.
- **Lo que falta para ser un producto vendible**, no solo un trabajo
  práctico funcional:
  - Registro de usuarios propio (hoy hay un único usuario fijo, pensado
    para la evaluación académica).
  - Multi-moneda, si se quisiera vender fuera de Argentina.
  - Un plan de monetización definido (hoy no existe ninguno: es
    software académico, no un producto con modelo de negocio).
  - Rotación de refresh tokens / blacklist (mejora de seguridad ya
    identificada en la auditoría técnica, pendiente por decisión de
    alcance del trabajo práctico, no por desconocimiento).

Este documento no promete un lanzamiento comercial: describe el
razonamiento de producto detrás de las decisiones ya tomadas, y es
honesto sobre la distancia entre "funciona y está bien hecho" y
"listo para vender".
