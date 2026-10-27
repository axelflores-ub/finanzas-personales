<script setup>
import { computed, onMounted, ref } from 'vue'

import { listCategorias } from '../api/categorias'
import {
  createMovimiento,
  deleteMovimiento,
  listMovimientos,
  updateMovimiento,
} from '../api/movimientos'
import MovimientoFormModal from '../components/movimientos/MovimientoFormModal.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import { formatFecha, formatMonto } from '../utils/format'

const movimientos = ref([])
const categorias = ref([])
const loading = ref(true)
const loadError = ref('')

const feedback = ref(null)
let feedbackTimer = null

const showForm = ref(false)
const editingMovimiento = ref(null)
const formSaving = ref(false)
const formError = ref('')

const showConfirm = ref(false)
const deletingMovimiento = ref(null)

const filtroFechaDesde = ref('')
const filtroFechaHasta = ref('')
const filtroTipo = ref('')
const filtroCategoria = ref('')
const filtroError = ref('')

const categoriasFiltro = computed(() => {
  if (!filtroTipo.value) return categorias.value
  return categorias.value.filter((categoria) => categoria.tipo === filtroTipo.value)
})

function onFiltroTipoChange() {
  const sigueDisponible = categoriasFiltro.value.some(
    (categoria) => String(categoria.id) === String(filtroCategoria.value),
  )
  if (!sigueDisponible) filtroCategoria.value = ''
}

async function cargarCategorias() {
  const { data } = await listCategorias()
  categorias.value = data
}

async function cargarMovimientos() {
  loading.value = true
  loadError.value = ''
  filtroError.value = ''
  try {
    const filtros = {}
    if (filtroFechaDesde.value) filtros.fecha_desde = filtroFechaDesde.value
    if (filtroFechaHasta.value) filtros.fecha_hasta = filtroFechaHasta.value
    if (filtroTipo.value) filtros.tipo = filtroTipo.value
    if (filtroCategoria.value) filtros.categoria = filtroCategoria.value

    const { data } = await listMovimientos(filtros)
    movimientos.value = data
  } catch (error) {
    if (error.response?.status === 400) {
      filtroError.value = extractErrorMessage(error, 'Filtros inválidos.')
      movimientos.value = []
    } else {
      loadError.value = 'No se pudieron cargar los movimientos. Reintentá más tarde.'
    }
  } finally {
    loading.value = false
  }
}

function limpiarFiltros() {
  filtroFechaDesde.value = ''
  filtroFechaHasta.value = ''
  filtroTipo.value = ''
  filtroCategoria.value = ''
  cargarMovimientos()
}

onMounted(async () => {
  await cargarCategorias()
  await cargarMovimientos()
})

function openCreateForm() {
  editingMovimiento.value = null
  formError.value = ''
  showForm.value = true
}

function openEditForm(movimiento) {
  editingMovimiento.value = movimiento
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
    if (editingMovimiento.value) {
      await updateMovimiento(editingMovimiento.value.id, payload)
      showFeedback('success', 'Movimiento actualizado correctamente.')
    } else {
      await createMovimiento(payload)
      showFeedback('success', 'Movimiento registrado correctamente.')
    }
    showForm.value = false
    await cargarMovimientos()
  } catch (error) {
    formError.value = extractErrorMessage(error, 'No se pudo guardar el movimiento.')
  } finally {
    formSaving.value = false
  }
}

function askDelete(movimiento) {
  deletingMovimiento.value = movimiento
  showConfirm.value = true
}

async function confirmDelete() {
  const movimiento = deletingMovimiento.value
  showConfirm.value = false
  try {
    await deleteMovimiento(movimiento.id)
    showFeedback('success', 'Movimiento eliminado.')
    await cargarMovimientos()
  } catch (error) {
    showFeedback('danger', extractErrorMessage(error, 'No se pudo eliminar el movimiento.'))
  } finally {
    deletingMovimiento.value = null
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
        <h1 class="h3 mb-1">Movimientos</h1>
        <p class="text-muted mb-0">Registrá y consultá tus ingresos y gastos.</p>
      </div>
      <button type="button" class="btn btn-primary" @click="openCreateForm">
        + Nuevo movimiento
      </button>
    </div>

    <transition name="fade">
      <div v-if="feedback" class="alert" :class="`alert-${feedback.type}`" role="alert">
        {{ feedback.message }}
      </div>
    </transition>

    <div class="card shadow-sm border-0 mb-3">
      <div class="card-body">
        <div v-if="filtroError" class="alert alert-danger py-2 small mb-3">
          {{ filtroError }}
        </div>
        <div class="row g-2 align-items-end">
          <div class="col-6 col-md-2">
            <label class="form-label small mb-1" for="filtro-fecha-desde">Desde</label>
            <input
              id="filtro-fecha-desde"
              v-model="filtroFechaDesde"
              type="date"
              class="form-control form-control-sm"
            />
          </div>
          <div class="col-6 col-md-2">
            <label class="form-label small mb-1" for="filtro-fecha-hasta">Hasta</label>
            <input
              id="filtro-fecha-hasta"
              v-model="filtroFechaHasta"
              type="date"
              class="form-control form-control-sm"
            />
          </div>
          <div class="col-6 col-md-2">
            <label class="form-label small mb-1" for="filtro-tipo">Tipo</label>
            <select
              id="filtro-tipo"
              v-model="filtroTipo"
              class="form-select form-select-sm"
              @change="onFiltroTipoChange"
            >
              <option value="">Todos</option>
              <option value="INGRESO">Ingreso</option>
              <option value="GASTO">Gasto</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label small mb-1" for="filtro-categoria">Categoría</label>
            <select id="filtro-categoria" v-model="filtroCategoria" class="form-select form-select-sm">
              <option value="">Todas</option>
              <option
                v-for="categoria in categoriasFiltro"
                :key="categoria.id"
                :value="categoria.id"
              >
                {{ categoria.nombre }}
              </option>
            </select>
          </div>
          <div class="col-12 col-md-3 d-flex gap-2">
            <button type="button" class="btn btn-sm btn-primary flex-fill" @click="cargarMovimientos">
              Filtrar
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary flex-fill" @click="limpiarFiltros">
              Limpiar
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0">
        <div v-if="loading" class="p-5 text-center text-muted">
          <div class="spinner-border spinner-border-sm me-2" role="status"></div>
          Cargando movimientos...
        </div>

        <div v-else-if="loadError" class="p-5 text-center text-danger">
          {{ loadError }}
        </div>

        <div v-else-if="movimientos.length === 0" class="p-5 text-center text-muted">
          No hay movimientos para los filtros seleccionados.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Categoría</th>
                <th>Tipo</th>
                <th class="text-end">Monto</th>
                <th class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="movimiento in movimientos" :key="movimiento.id">
                <td>{{ formatFecha(movimiento.fecha) }}</td>
                <td class="text-muted">{{ movimiento.descripcion || '—' }}</td>
                <td>{{ movimiento.categoria_nombre }}</td>
                <td>
                  <span
                    class="badge rounded-pill"
                    :class="movimiento.tipo === 'INGRESO' ? 'text-bg-success' : 'text-bg-danger'"
                  >
                    {{ movimiento.tipo === 'INGRESO' ? 'Ingreso' : 'Gasto' }}
                  </span>
                </td>
                <td
                  class="text-end fw-semibold"
                  :class="movimiento.tipo === 'INGRESO' ? 'text-success' : 'text-danger'"
                >
                  {{ formatMonto(movimiento.monto) }}
                </td>
                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary me-2"
                    @click="openEditForm(movimiento)"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    @click="askDelete(movimiento)"
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

    <MovimientoFormModal
      :show="showForm"
      :movimiento="editingMovimiento"
      :categorias="categorias"
      :saving="formSaving"
      :error-message="formError"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <ConfirmDialog
      :show="showConfirm"
      title="Eliminar movimiento"
      message="¿Seguro que querés eliminar este movimiento? Esta acción no se puede deshacer."
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
