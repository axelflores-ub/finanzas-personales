import { defineStore } from 'pinia'

import authClient from '../api/authClient'

// Sesión simple: access y refresh token viven solo en memoria (estado de
// Pinia), nunca en localStorage/sessionStorage. Ventaja: nada queda
// expuesto a un ataque XSS vía storage. Limitación documentada: recargar
// la página (F5) cierra la sesión, porque el estado de JS se reinicia.
export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    refreshToken: null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(username, password) {
      const { data } = await authClient.post('/auth/token/', { username, password })
      this.accessToken = data.access
      this.refreshToken = data.refresh
      await this.fetchUser()
    },

    async fetchUser() {
      const { data } = await authClient.get('/auth/me/', {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      })
      this.user = data
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        throw new Error('No hay sesión activa para refrescar.')
      }
      const { data } = await authClient.post('/auth/token/refresh/', {
        refresh: this.refreshToken,
      })
      this.accessToken = data.access
      return this.accessToken
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
    },
  },
})
