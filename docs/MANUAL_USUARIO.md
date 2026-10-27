# Manual de usuario

Guía de uso del Sistema de Gestión de Finanzas Personales. No requiere
conocimientos de programación — solo saber usar un navegador web.

## Índice

1. [Iniciar sesión](#1-iniciar-sesión)
2. [Navegar por el sistema](#2-navegar-por-el-sistema)
3. [Categorías](#3-categorías)
4. [Movimientos (ingresos y gastos)](#4-movimientos-ingresos-y-gastos)
5. [Dashboard](#5-dashboard)
6. [Presupuestos](#6-presupuestos)
7. [Errores y mensajes de validación](#7-errores-y-mensajes-de-validación)
8. [Cerrar sesión](#8-cerrar-sesión)
9. [Limitaciones a tener en cuenta](#9-limitaciones-a-tener-en-cuenta)

## 1. Iniciar sesión

Al abrir la aplicación en el navegador, se muestra la pantalla de login
con dos campos: **usuario** y **contraseña**.

- Ingresá tus credenciales y hacé clic en **Ingresar**.
- Si los datos son incorrectos, aparece un mensaje de error debajo del
  formulario y podés volver a intentarlo.
- Si todo está bien, el sistema te lleva directo al **Dashboard**.

> El sistema no tiene un botón de "Registrarse": el usuario se crea una
> sola vez al instalar la aplicación. Si no tenés credenciales, consultá a
> quien administra la instalación.

## 2. Navegar por el sistema

Una vez dentro, en el margen izquierdo hay un menú fijo con cuatro
secciones:

- **Dashboard** — resumen general de tu situación financiera.
- **Categorías** — tipos de ingreso/gasto que usás para clasificar.
- **Movimientos** — el detalle de cada ingreso o gasto registrado.
- **Presupuestos** — límites de gasto mensual por categoría.

Debajo del menú se ve tu nombre de usuario y el botón **Cerrar sesión**.
Al hacer clic en cualquiera de las cuatro secciones, el contenido
principal (a la derecha) cambia; el menú siempre queda visible.

En pantallas chicas (celular), el diseño se adapta y las tarjetas se
acomodan una debajo de la otra en vez de en columnas.

## 3. Categorías

Las categorías son las "etiquetas" con las que vas a clasificar cada
ingreso o gasto (por ejemplo: "Sueldo", "Alimentación", "Transporte").
Cada categoría es de un único tipo: **Ingreso** o **Gasto**.

### Crear una categoría

1. Entrá a **Categorías** en el menú.
2. Hacé clic en **+ Nueva categoría**.
3. Completá el **nombre** y elegí el **tipo** (Ingreso o Gasto).
4. Hacé clic en **Guardar**.

Si ya existe una categoría con ese mismo nombre y tipo, el sistema no la
crea y muestra un aviso explicando por qué.

### Editar una categoría

Hacé clic en **Editar** en la fila de la categoría que querés modificar,
cambiá lo que necesites y guardá. Vale la misma regla: no puede quedar
duplicada con otra categoría tuya.

### Eliminar una categoría

Hacé clic en **Eliminar** y confirmá en el cuadro de diálogo que aparece.

> Si la categoría tiene movimientos o presupuestos asociados, el sistema
> **no la deja borrar** y muestra un mensaje explicándolo. Primero hay que
> borrar (o reasignar) esos movimientos/presupuestos.

## 4. Movimientos (ingresos y gastos)

Un "movimiento" es cada ingreso o gasto puntual: un sueldo cobrado, una
compra, un pago de servicio, etc.

### Registrar un movimiento

1. Entrá a **Movimientos**.
2. Hacé clic en **+ Nuevo movimiento**.
3. Elegí el **tipo** (Ingreso o Gasto) — esto filtra automáticamente las
   categorías disponibles para que elijas una acorde.
4. Elegí la **categoría**, ingresá el **monto**, la **fecha** y,
   opcionalmente, una **descripción**.
5. Hacé clic en **Guardar**.

Si no tenés ninguna categoría creada para el tipo elegido, el formulario
te avisa y no te deja guardar hasta que crees una en **Categorías**.

### Editar o eliminar un movimiento

En la tabla de movimientos, cada fila tiene botones **Editar** y
**Eliminar**. Eliminar pide confirmación antes de borrar definitivamente.

### Filtrar movimientos

Arriba de la tabla hay un panel de filtros, todos opcionales y
combinables entre sí:

- **Desde** / **Hasta**: rango de fechas.
- **Tipo**: Ingreso, Gasto, o Todos.
- **Categoría**: se ajusta según el tipo elegido.

Hacé clic en **Filtrar** para aplicar, o **Limpiar** para volver a ver
todos los movimientos.

## 5. Dashboard

Es la pantalla de inicio y da una foto completa de tu situación
financiera para el mes y año que elijas arriba a la derecha (por defecto,
el mes actual).

- **Tarjetas superiores**: Ingresos totales, Gastos totales y Balance
  disponible (ingresos menos gastos) del período elegido. El balance se
  muestra en verde si es positivo y en rojo si es negativo.
- **Gráfico de gastos por categoría** (dona): muestra qué proporción de
  tus gastos del período corresponde a cada categoría. Pasando el mouse
  sobre cada porción se ve el monto exacto y el porcentaje. Si no
  registraste gastos en el período, se muestra un aviso en lugar del
  gráfico.
- **Gráfico de evolución mensual**: barras comparando ingresos (verde) y
  gastos (rojo) mes por mes durante todo el año seleccionado. Sirve para
  ver tendencias (por ejemplo, si los gastos vienen subiendo).
- **Presupuestos del período**: un resumen rápido de cuánto presupuesto
  total definiste, cuánto gastaste realmente en esas categorías
  presupuestadas, y una barra de progreso con el porcentaje utilizado.
  Hay un enlace **Ver detalle →** que te lleva a la sección completa de
  Presupuestos.

Para ver otro mes o año, usá los selectores de arriba — el contenido se
actualiza automáticamente.

## 6. Presupuestos

Un presupuesto es un límite de gasto que te ponés a vos mismo para una
categoría en un mes y año puntuales (por ejemplo: "no gastar más de
$50.000 en Alimentación en octubre 2026"). Solo se pueden presupuestar
categorías de tipo **Gasto** (no tiene sentido presupuestar un ingreso).

### Crear un presupuesto

1. Entrá a **Presupuestos**.
2. Elegí el mes y año que querés ver (arriba a la derecha).
3. Hacé clic en **+ Nuevo presupuesto**.
4. Elegí la categoría de gasto, confirmá el mes/año, e ingresá el
   **límite** en pesos.
5. Guardá.

No se puede crear dos presupuestos para la misma categoría en el mismo
mes y año — si lo intentás, el sistema lo rechaza y te avisa.

### Interpretar el porcentaje de presupuesto utilizado

Cada tarjeta de presupuesto muestra una barra de progreso con tres
colores, según cuánto llevás gastado respecto del límite que pusiste:

- 🟢 **Verde** (menos del 80%): vas bien, margen disponible.
- 🟡 **Amarillo** (entre 80% y 99%): te estás acercando al límite.
- 🔴 **Rojo** (100% o más): llegaste o superaste el límite. En este caso,
  en vez de mostrar un monto "restante" negativo y confuso, el sistema
  muestra **"Excedido en $X"** con el monto que te pasaste.

El gasto real de cada presupuesto se recalcula automáticamente cada vez
que entrás a la pantalla: si agregás, editás o borrás un movimiento de
esa categoría en ese período, el porcentaje se actualiza solo, sin que
tengas que hacer nada manualmente.

### Editar o eliminar un presupuesto

Igual que en Categorías y Movimientos: botones **Editar**/**Eliminar** en
cada tarjeta, con confirmación antes de borrar.

## 7. Errores y mensajes de validación

Cuando algo no se puede guardar, el sistema **no deja la pantalla en
blanco ni se cuelga**: muestra un mensaje explicando qué pasó, cerca del
campo o del formulario correspondiente. Ejemplos:

- Monto en cero o negativo → "el monto debe ser mayor a 0" (no se guarda
  nada, el dato anterior queda intacto si estabas editando).
- Categoría duplicada → aviso de que ya existe una con ese nombre y tipo.
- Presupuesto duplicado → aviso de que ya existe uno para esa categoría
  en ese período.
- Intentar borrar una categoría en uso → aviso de que tiene movimientos o
  presupuestos asociados.
- Filtros de fecha con el rango invertido (desde posterior a hasta) →
  aviso explicando el problema, sin romper la lista de movimientos.
- Pérdida de conexión con el servidor → mensaje genérico pidiendo
  reintentar más tarde.

Ante cualquier error, los datos que ya tenías guardados **nunca se
alteran**: una operación rechazada no modifica nada a medias.

## 8. Cerrar sesión

Hacé clic en **Cerrar sesión**, al pie del menú lateral. Te vuelve a la
pantalla de login.

> **Importante**: recargar la página (F5) o cerrar la pestaña también
> cierra la sesión — no hace falta tocar "Cerrar sesión" para eso. Ver la
> siguiente sección.

## 9. Limitaciones a tener en cuenta

- **Recargar la página cierra la sesión.** Es una decisión de seguridad
  del sistema (la sesión no se guarda en el navegador, solo en la memoria
  de la pestaña abierta), no un error. Si te pasa, simplemente volvés a
  iniciar sesión.
- **No hay registro de usuarios nuevos** desde la aplicación: el usuario
  se crea una sola vez al instalar el sistema.
- **No hay opción de elegir otra moneda**: todos los montos se asumen en
  pesos argentinos.
- Si tu sesión queda inactiva mucho tiempo (más de una hora sin usar la
  app) y además se cumplen 7 días desde el último login, el sistema te
  desloguea automáticamente y te pide volver a iniciar sesión.
