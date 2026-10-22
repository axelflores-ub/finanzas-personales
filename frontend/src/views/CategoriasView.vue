<script setup>
import { onMounted, ref } from 'vue'

import {
  createCategoria,
  deleteCategoria,
  listCategorias,
  updateCategoria,
} from '../api/categorias'
import CategoriaFormModal from '../components/categorias/CategoriaFormModal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'

const categorias = ref([])
const loading = ref(true)
const loadError = ref('')

const feedback = ref(null) // { type: 'success' | 'danger', message: string }
let feedbackTimer = null

const showForm = ref(false)
const editingCategoria = ref(null)
const formSaving = ref(false)
const formError = ref('')

const showConfirm = ref(false)
const deletingCategoria = ref(null)

async function loadCategorias() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await listCategorias()
    categorias.value = data
  } catch {
    loadError.value = 'No se pudieron cargar las categorías. Reintentá más tarde.'
  } finally {
    loading.value = false
  }
}

onMounted(loadCategorias)

function openCreateForm() {
  editingCategoria.value = null
  formError.value = ''
  showForm.value = true
}

function openEditForm(categoria) {
  editingCategoria.value = categoria
  formError.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

async function handleFormSubmit(payload) {
  formSaving.value = true
  formError.value = ''
  try {
    if (editingCategoria.value) {
      await updateCategoria(editingCategoria.value.id, payload)
      showFeedback('success', 'Categoría actualizada correctamente.')
    } else {
      await createCategoria(payload)
      showFeedback('success', 'Categoría creada correctamente.')
    }
    showForm.value = false
    await loadCategorias()
  } catch (error) {
    formError.value = extractErrorMessage(error, 'No se pudo guardar la categoría.')
  } finally {
    formSaving.value = false
  }
}

function askDelete(categoria) {
  deletingCategoria.value = categoria
  showConfirm.value = true
}

async function confirmDelete() {
  const categoria = deletingCategoria.value
  showConfirm.value = false
  try {
    await deleteCategoria(categoria.id)
    showFeedback('success', 'Categoría eliminada.')
    await loadCategorias()
  } catch (error) {
    showFeedback('danger', extractErrorMessage(error, 'No se pudo eliminar la categoría.'))
  } finally {
    deletingCategoria.value = null
  }
}

function showFeedback(type, message) {
  feedback.value = { type, message }
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => {
    feedback.value = null
  }, 4000)
}

function extractErrorMessage(error, fallback) {
  const data = error.response?.data
  if (data?.detail) return data.detail
  if (data) {
    const firstKey = Object.keys(data)[0]
    const value = data[firstKey]
    if (Array.isArray(value)) return value[0]
    if (typeof value === 'string') return value
  }
  return fallback
}

function tipoLabel(tipo) {
  return tipo === 'INGRESO' ? 'Ingreso' : 'Gasto'
}
</script>

<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h1 class="h3 mb-1">Categorías</h1>
        <p class="text-muted mb-0">Organizá tus ingresos y gastos por categoría.</p>
      </div>
      <button type="button" class="btn btn-primary" @click="openCreateForm">
        + Nueva categoría
      </button>
    </div>

    <transition name="fade">
      <div v-if="feedback" class="alert" :class="`alert-${feedback.type}`" role="alert">
        {{ feedback.message }}
      </div>
    </transition>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0">
        <div v-if="loading" class="p-5 text-center text-muted">
          <div class="spinner-border spinner-border-sm me-2" role="status"></div>
          Cargando categorías...
        </div>

        <div v-else-if="loadError" class="p-5 text-center text-danger">
          {{ loadError }}
        </div>

        <div v-else-if="categorias.length === 0" class="p-5 text-center text-muted">
          Todavía no tenés categorías. Creá la primera con el botón de arriba.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Tipo</th>
                <th class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="categoria in categorias" :key="categoria.id">
                <td>{{ categoria.nombre }}</td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="categoria.tipo === 'INGRESO' ? 'text-bg-success' : 'text-bg-danger'"
                  >
                    {{ tipoLabel(categoria.tipo) }}
                  </span>
                </td>
                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary me-2"
                    @click="openEditForm(categoria)"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    @click="askDelete(categoria)"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <CategoriaFormModal
      :show="showForm"
      :categoria="editingCategoria"
      :saving="formSaving"
      :error-message="formError"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <ConfirmDialog
      :show="showConfirm"
      title="Eliminar categoría"
      :message="`¿Seguro que querés eliminar '${deletingCategoria?.nombre}'? Esta acción no se puede deshacer.`"
      confirm-label="Eliminar"
      confirm-variant="danger"
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
