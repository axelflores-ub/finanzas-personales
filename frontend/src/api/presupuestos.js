import apiClient from './axios'

export function listPresupuestos(mes, anio) {
  return apiClient.get('/presupuestos/', { params: { mes, anio } })
}

export function createPresupuesto(payload) {
  return apiClient.post('/presupuestos/', payload)
}

export function updatePresupuesto(id, payload) {
  return apiClient.patch(`/presupuestos/${id}/`, payload)
}

export function deletePresupuesto(id) {
  return apiClient.delete(`/presupuestos/${id}/`)
}
