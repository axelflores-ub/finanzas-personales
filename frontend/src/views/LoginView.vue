<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const sessionExpired = route.query.expired === '1'

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    const redirectTo = typeof route.query.redirect === 'string' ? route.query.redirect : null
    router.push(redirectTo ?? { name: 'categorias' })
  } catch (error) {
    if (error.response?.status === 401) {
      errorMessage.value = 'Usuario o contraseña incorrectos.'
    } else {
      errorMessage.value = 'No se pudo iniciar sesión. Intentá nuevamente.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page d-flex align-items-center justify-content-center">
    <div class="card login-card shadow">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div class="brand-mark mx-auto mb-3">$</div>
          <h1 class="h4 mb-1">Finanzas Personales</h1>
          <p class="text-muted mb-0">Iniciá sesión para continuar</p>
        </div>

        <div v-if="sessionExpired" class="alert alert-warning py-2 small">
          Tu sesión expiró. Volvé a iniciar sesión.
        </div>

        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label" for="username">Usuario</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="form-control"
              autocomplete="username"
              required
            />
          </div>
          <div class="mb-3">
            <label class="form-label" for="password">Contraseña</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-control"
              autocomplete="current-password"
              required
            />
          </div>

          <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
            {{ errorMessage }}
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Ingresar
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #14213d 0%, #1b2f5e 100%);
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border: none;
  border-radius: 16px;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #fca311;
  color: #14213d;
  font-weight: 700;
  font-size: 1.25rem;
}
</style>
