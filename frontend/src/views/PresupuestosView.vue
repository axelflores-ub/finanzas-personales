<script setup>
import { computed, onMounted, ref } from 'vue'

import { listCategorias } from '../api/categorias'
import {
  createPresupuesto,
  deletePresupuesto,
  listPresupuestos,
  updatePresupuesto,
} from '../api/presupuestos'
import PresupuestoFormModal from '../components/presupuestos/PresupuestoFormModal.vue'
import PresupuestoCard from '../components/presupuestos/PresupuestoCard.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import { MESES, aniosDisponibles, formatMonto } from '../utils/format'

const hoy = new Date()
const mes = ref(hoy.getMonth() + 1)
const anio = ref(hoy.getFullYear())

const presupuestos = ref([])
const categorias = ref([])
const loading = ref(true)
const loadError = ref('')

const feedback = ref(null)
let feedbackTimer = null

const showForm = ref(false)
const editingPresupuesto = ref(null)
const formSaving = ref(false)
const formError = ref('')

const showConfirm = ref(false)
const deletingPresupuesto = ref(null)

const categoriasGasto = computed(() => categorias.value.filter((c) => c.tipo === 'GASTO'))

const totales = computed(() => {
  const presupuestoTotal = presupuestos.value.reduce(
    (acc, p) => acc + Number(p.monto_limite),
    0,
  )
  const gastoReal = presupuestos.value.reduce((acc, p) => acc + Number(p.gasto_real), 0)
  return {
    presupuestoTotal,
    gastoReal,
    disponible: presupuestoTotal - gastoReal,
  }
})

async function cargarCategorias() {
  const { data } = await listCategorias()
  categorias.value = data
}

// Id incremental para descartar respuestas obsoletas ante cambios rápidos
// de mes/año (mismo mecanismo que en DashboardView.vue).
let presupuestosRequestId = 0

async function cargarPresupuestos() {
  const requestId = ++presupuestosRequestId
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await listPresupuestos(mes.value, anio.value)
    if (requestId !== presupuestosRequestId) return
    presupuestos.value = data
  } catch {
    if (requestId !== presupuestosRequestId) return
    loadError.value = 'No se pudieron cargar los presupuestos. Reintentá más tarde.'
    presupuestos.value = []
  } finally {
    if (requestId === presupuestosRequestId) loading.value = false
  }
}

onMounted(async () => {
  await cargarCategorias()
  await cargarPresupuestos()
})

function openCreateForm() {
  editingPresupuesto.value = null
  formError.value = ''
  showForm.value = true
}

function openEditForm(presupuesto) {
  editingPresupuesto.value = presupuesto
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
    if (editingPresupuesto.value) {
      await updatePresupuesto(editingPresupuesto.value.id, payload)
      showFeedback('success', 'Presupuesto actualizado correctamente.')
    } else {
      await createPresupuesto(payload)
      showFeedback('success', 'Presupuesto creado correctamente.')
    }
    showForm.value = false
    await cargarPresupuestos()
  } catch (error) {
    formError.value = extractErrorMessage(error, 'No se pudo guardar el presupuesto.')
  } finally {
    formSaving.value = false
  }
}

function askDelete(presupuesto) {
  deletingPresupuesto.value = presupuesto
  showConfirm.value = true
}

async function confirmDelete() {
  const presupuesto = deletingPresupuesto.value
  showConfirm.value = false
  try {
    await deletePresupuesto(presupuesto.id)
    showFeedback('success', 'Presupuesto eliminado.')
    await cargarPresupuestos()
  } catch (error) {
    showFeedback('danger', extractErrorMessage(error, 'No se pudo eliminar el presupuesto.'))
  } finally {
    deletingPresupuesto.value = null
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
</script>

<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h1 class="h3 mb-1">Presupuestos</h1>
        <p class="text-muted mb-0">Definí límites de gasto por categoría y seguí su uso.</p>
      </div>
      <div class="d-flex gap-2 align-items-center flex-wrap">
        <select
          v-model.number="mes"
          class="form-select form-select-sm w-auto"
          aria-label="Mes"
          @change="cargarPresupuestos"
        >
          <option v-for="(nombre, index) in MESES" :key="nombre" :value="index + 1">
            {{ nombre }}
          </option>
        </select>
        <select
          v-model.number="anio"
          class="form-select form-select-sm w-auto"
          aria-label="Año"
          @change="cargarPresupuestos"
        >
          <option v-for="a in aniosDisponibles()" :key="a" :value="a">{{ a }}</option>
        </select>
        <button type="button" class="btn btn-primary" @click="openCreateForm">
          + Nuevo presupuesto
        </button>
      </div>
    </div>

    <transition name="fade">
      <div v-if="feedback" class="alert" :class="`alert-${feedback.type}`" role="alert">
        {{ feedback.message }}
      </div>
    </transition>

    <div v-if="!loading && !loadError && presupuestos.length > 0" class="row g-3 mb-4">
      <div class="col-12 col-md-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body">
            <div class="text-muted small mb-1">Presupuesto total</div>
            <div class="h4 mb-0">{{ formatMonto(totales.presupuestoTotal) }}</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body">
            <div class="text-muted small mb-1">Gasto real</div>
            <div class="h4 mb-0">{{ formatMonto(totales.gastoReal) }}</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body">
            <div class="text-muted small mb-1">Disponible</div>
            <div class="h4 mb-0" :class="totales.disponible < 0 ? 'text-danger' : 'text-success'">
              {{ formatMonto(totales.disponible) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="p-5 text-center text-muted">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      Cargando presupuestos...
    </div>

    <div v-else-if="loadError" class="alert alert-danger">{{ loadError }}</div>

    <div v-else-if="presupuestos.length === 0" class="card shadow-sm border-0">
      <div class="card-body p-5 text-center text-muted">
        No definiste presupuestos para este período. Creá el primero con el botón de arriba.
      </div>
    </div>

    <div v-else>
      <PresupuestoCard
        v-for="presupuesto in presupuestos"
        :key="presupuesto.id"
        :presupuesto="presupuesto"
        @editar="openEditForm"
        @eliminar="askDelete"
      />
    </div>

    <PresupuestoFormModal
      :show="showForm"
      :presupuesto="editingPresupuesto"
      :categorias-gasto="categoriasGasto"
      :mes-por-defecto="mes"
      :anio-por-defecto="anio"
      :saving="formSaving"
      :error-message="formError"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <ConfirmDialog
      :show="showConfirm"
      title="Eliminar presupuesto"
      :message="`¿Seguro que querés eliminar el presupuesto de '${deletingPresupuesto?.categoria_nombre}'? Esta acción no se puede deshacer.`"
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
