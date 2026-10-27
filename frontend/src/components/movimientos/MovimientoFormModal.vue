<script setup>
import { computed, ref, watch } from 'vue'

import { useModalA11y } from '../../composables/useModalA11y'
import { fechaHoy } from '../../utils/format'

const props = defineProps({
  show: { type: Boolean, default: false },
  movimiento: { type: Object, default: null }, // null = crear, objeto = editar
  categorias: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const tipo = ref('GASTO')
const categoriaId = ref('')
const monto = ref('')
const fecha = ref('')
const descripcion = ref('')

const modalRef = ref(null)
useModalA11y(
  computed(() => props.show),
  modalRef,
  () => emit('cancel'),
)

const categoriasFiltradas = computed(() =>
  props.categorias.filter((categoria) => categoria.tipo === tipo.value),
)

function categoriaPorDefecto(tipoSeleccionado) {
  return props.categorias.find((categoria) => categoria.tipo === tipoSeleccionado)?.id ?? ''
}

watch(
  () => props.show,
  (isOpen) => {
    if (!isOpen) return
    if (props.movimiento) {
      tipo.value = props.movimiento.tipo
      categoriaId.value = props.movimiento.categoria
      monto.value = props.movimiento.monto
      fecha.value = props.movimiento.fecha
      descripcion.value = props.movimiento.descripcion ?? ''
    } else {
      tipo.value = 'GASTO'
      categoriaId.value = categoriaPorDefecto('GASTO')
      monto.value = ''
      fecha.value = fechaHoy()
      descripcion.value = ''
    }
  },
  { immediate: true },
)

// Corre también cuando el usuario cambia el tipo a mano: si la categoría
// elegida no es del nuevo tipo (o no había ninguna, ver bug de la primera
// apertura con el tipo por defecto sin cambios), se recalcula.
watch(tipo, (nuevoTipo) => {
  const sigueDisponible = categoriasFiltradas.value.some(
    (categoria) => categoria.id === categoriaId.value,
  )
  if (!sigueDisponible) {
    categoriaId.value = categoriaPorDefecto(nuevoTipo)
  }
})

function handleSubmit() {
  emit('submit', {
    categoria: categoriaId.value,
    monto: monto.value,
    fecha: fecha.value,
    descripcion: descripcion.value.trim(),
  })
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom" @click.self="emit('cancel')">
    <div ref="modalRef" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <form @submit.prevent="handleSubmit" novalidate>
            <div class="modal-header">
              <h5 class="modal-title">
                {{ movimiento ? 'Editar movimiento' : 'Nuevo movimiento' }}
              </h5>
              <button
                type="button"
                class="btn-close"
                aria-label="Cerrar"
                @click="emit('cancel')"
              ></button>
            </div>
            <div class="modal-body">
              <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
                {{ errorMessage }}
              </div>

              <div class="mb-3">
                <label class="form-label d-block">Tipo</label>
                <div class="btn-group w-100" role="group">
                  <input
                    id="tipo-gasto"
                    v-model="tipo"
                    type="radio"
                    class="btn-check"
                    value="GASTO"
                  />
                  <label class="btn btn-outline-danger" for="tipo-gasto">Gasto</label>

                  <input
                    id="tipo-ingreso"
                    v-model="tipo"
                    type="radio"
                    class="btn-check"
                    value="INGRESO"
                  />
                  <label class="btn btn-outline-success" for="tipo-ingreso">Ingreso</label>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label" for="movimiento-categoria">Categoría</label>
                <select
                  id="movimiento-categoria"
                  v-model="categoriaId"
                  class="form-select"
                  required
                  :disabled="categoriasFiltradas.length === 0"
                >
                  <option
                    v-for="categoria in categoriasFiltradas"
                    :key="categoria.id"
                    :value="categoria.id"
                  >
                    {{ categoria.nombre }}
                  </option>
                </select>
                <div v-if="categoriasFiltradas.length === 0" class="form-text text-danger">
                  No tenés categorías de tipo
                  {{ tipo === 'INGRESO' ? 'Ingreso' : 'Gasto' }}. Creá una primero en Categorías.
                </div>
              </div>

              <div class="row">
                <div class="col-6 mb-3">
                  <label class="form-label" for="movimiento-monto">Monto</label>
                  <input
                    id="movimiento-monto"
                    v-model="monto"
                    type="number"
                    class="form-control"
                    step="0.01"
                    min="0.01"
                    required
                  />
                </div>
                <div class="col-6 mb-3">
                  <label class="form-label" for="movimiento-fecha">Fecha</label>
                  <input
                    id="movimiento-fecha"
                    v-model="fecha"
                    type="date"
                    class="form-control"
                    required
                  />
                </div>
              </div>

              <div class="mb-1">
                <label class="form-label" for="movimiento-descripcion">
                  Descripción <span class="text-muted">(opcional)</span>
                </label>
                <input
                  id="movimiento-descripcion"
                  v-model="descripcion"
                  type="text"
                  class="form-control"
                  maxlength="255"
                />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="emit('cancel')">
                Cancelar
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="saving || categoriasFiltradas.length === 0"
              >
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                Guardar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 1055;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
</style>
