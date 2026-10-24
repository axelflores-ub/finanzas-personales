import apiClient from './axios'

export function getResumen(mes, anio) {
  return apiClient.get('/dashboard/resumen/', { params: { mes, anio } })
}

export function getGastosPorCategoria(mes, anio) {
  return apiClient.get('/dashboard/gastos-por-categoria/', { params: { mes, anio } })
}

export function getPresupuestosResumen(mes, anio) {
  return apiClient.get('/dashboard/presupuestos-resumen/', { params: { mes, anio } })
}
