export const MESES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

export const MESES_CORTOS = MESES.map((mes) => mes.slice(0, 3))

export function aniosDisponibles() {
  const actual = new Date().getFullYear()
  const anios = []
  for (let a = actual - 3; a <= actual + 1; a++) anios.push(a)
  return anios
}

const currencyFormatter = new Intl.NumberFormat('es-AR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

// Formato argentino explícito ("$ 25.000,00"): no se usa
// Intl...{style:'currency'} porque el símbolo/espaciado que genera varía
// según el entorno; armamos el prefijo "$ " a mano para que sea estable.
export function formatMonto(value) {
  const numero = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(numero)) return '$ 0,00'
  return `$ ${currencyFormatter.format(numero)}`
}

export function formatFecha(isoDate) {
  if (!isoDate) return ''
  const [anio, mes, dia] = isoDate.split('-')
  return `${dia}/${mes}/${anio}`
}

export function fechaHoy() {
  const hoy = new Date()
  const anio = hoy.getFullYear()
  const mes = String(hoy.getMonth() + 1).padStart(2, '0')
  const dia = String(hoy.getDate()).padStart(2, '0')
  return `${anio}-${mes}-${dia}`
}

// Umbrales de uso de presupuesto: <80% normal, 80-99% advertencia, >=100% límite alcanzado/superado.
export function claseUtilizacion(porcentaje) {
  const valor = typeof porcentaje === 'string' ? Number(porcentaje) : porcentaje
  if (valor >= 100) return 'danger'
  if (valor >= 80) return 'warning'
  return 'success'
}
