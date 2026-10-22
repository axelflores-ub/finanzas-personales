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
