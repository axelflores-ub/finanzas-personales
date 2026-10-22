import apiClient from './axios'

export function listCategorias() {
  return apiClient.get('/categorias/')
}

export function createCategoria(payload) {
  return apiClient.post('/categorias/', payload)
}

export function updateCategoria(id, payload) {
  return apiClient.patch(`/categorias/${id}/`, payload)
}

export function deleteCategoria(id) {
  return apiClient.delete(`/categorias/${id}/`)
}
