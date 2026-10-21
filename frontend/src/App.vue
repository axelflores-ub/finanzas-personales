<script setup>
import { onMounted, ref } from 'vue'
import apiClient from './api/axios'

const status = ref('pending')
const detail = ref(null)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const response = await apiClient.get('/health/')
    detail.value = response.data
    status.value = 'ok'
  } catch (error) {
    status.value = 'error'
    errorMessage.value = error.message
  }
})
</script>

<template>
  <div class="container py-5">
    <h1 class="mb-4">Sistema de Gestión de Finanzas Personales</h1>

    <div v-if="status === 'pending'" class="alert alert-secondary">
      Verificando conexión con el backend...
    </div>

    <div v-else-if="status === 'ok'" class="alert alert-success">
      <strong>Conexión OK.</strong>
      Backend respondió: <code>{{ JSON.stringify(detail) }}</code>
    </div>

    <div v-else class="alert alert-danger">
      <strong>No se pudo conectar con el backend.</strong>
      {{ errorMessage }}
    </div>
  </div>
</template>
