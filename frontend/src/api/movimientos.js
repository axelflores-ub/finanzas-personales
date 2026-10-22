import apiClient from './axios'

export function listMovimientos(filtros = {}) {
  return apiClient.get('/movimientos/', { params: filtros })
}

export function createMovimiento(payload) {
  return apiClient.post('/movimientos/', payload)
}

export function updateMovimiento(id, payload) {
  return apiClient.patch(`/movimientos/${id}/`, payload)
}

export function deleteMovimiento(id) {
  return apiClient.delete(`/movimientos/${id}/`)
}
