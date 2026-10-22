import apiClient from './axios'

export function getResumen(mes, anio) {
  return apiClient.get('/dashboard/resumen/', { params: { mes, anio } })
}

export function getGastosPorCategoria(mes, anio) {
  return apiClient.get('/dashboard/gastos-por-categoria/', { params: { mes, anio } })
}
