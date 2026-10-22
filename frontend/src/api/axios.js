import axios from 'axios'

import router from '../router'
import { useAuthStore } from '../store/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise = null

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status

    if (status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error)
    }

    const authStore = useAuthStore()
    if (!authStore.refreshToken) {
      authStore.logout()
      redirectToLogin()
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      refreshPromise = refreshPromise ?? authStore.refreshAccessToken()
      const newAccessToken = await refreshPromise
      refreshPromise = null
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      refreshPromise = null
      authStore.logout()
      redirectToLogin()
      return Promise.reject(refreshError)
    }
  },
)

function redirectToLogin() {
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login', query: { expired: '1' } })
  }
}

export default apiClient
