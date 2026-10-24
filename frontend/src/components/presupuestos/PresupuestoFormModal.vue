<script setup>
import { ref, watch } from 'vue'

import { MESES, aniosDisponibles } from '../../utils/format'

const props = defineProps({
  show: { type: Boolean, default: false },
  presupuesto: { type: Object, default: null }, // null = crear, objeto = editar
  categoriasGasto: { type: Array, default: () => [] },
  mesPorDefecto: { type: Number, required: true },
  anioPorDefecto: { type: Number, required: true },
  saving: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const categoriaId = ref('')
const mes = ref(props.mesPorDefecto)
const anio = ref(props.anioPorDefecto)
const montoLimite = ref('')

watch(
  () => props.show,
  (isOpen) => {
    if (!isOpen) return
    if (props.presupuesto) {
      categoriaId.value = props.presupuesto.categoria
      mes.value = props.presupuesto.mes
      anio.value = props.presupuesto.anio
      montoLimite.value = props.presupuesto.monto_limite
    } else {
      categoriaId.value = props.categoriasGasto[0]?.id ?? ''
      mes.value = props.mesPorDefecto
      anio.value = props.anioPorDefecto
      montoLimite.value = ''
    }
  },
  { immediate: true },
)

function handleSubmit() {
  emit('submit', {
    categoria: categoriaId.value,
    mes: mes.value,
    anio: anio.value,
    monto_limite: montoLimite.value,
  })
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom" @click.self="emit('cancel')">
    <div class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <form @submit.prevent="handleSubmit" novalidate>
            <div class="modal-header">
              <h5 class="modal-title">
                {{ presupuesto ? 'Editar presupuesto' : 'Nuevo presupuesto' }}
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
                <label class="form-label" for="presupuesto-categoria">Categoría (Gasto)</label>
                <select
                  id="presupuesto-categoria"
                  v-model="categoriaId"
                  class="form-select"
                  required
                  :disabled="categoriasGasto.length === 0"
                >
                  <option v-for="categoria in categoriasGasto" :key="categoria.id" :value="categoria.id">
                    {{ categoria.nombre }}
                  </option>
                </select>
                <div v-if="categoriasGasto.length === 0" class="form-text text-danger">
                  No tenés categorías de tipo Gasto. Creá una primero en Categorías.
                </div>
              </div>

              <div class="row">
                <div class="col-6 mb-3">
                  <label class="form-label" for="presupuesto-mes">Mes</label>
                  <select id="presupuesto-mes" v-model.number="mes" class="form-select">
                    <option v-for="(nombre, index) in MESES" :key="nombre" :value="index + 1">
                      {{ nombre }}
                    </option>
                  </select>
                </div>
                <div class="col-6 mb-3">
                  <label class="form-label" for="presupuesto-anio">Año</label>
                  <select id="presupuesto-anio" v-model.number="anio" class="form-select">
                    <option v-for="a in aniosDisponibles()" :key="a" :value="a">{{ a }}</option>
                  </select>
                </div>
              </div>

              <div class="mb-1">
                <label class="form-label" for="presupuesto-monto">Límite</label>
                <input
                  id="presupuesto-monto"
                  v-model="montoLimite"
                  type="number"
                  class="form-control"
                  step="0.01"
                  min="0.01"
                  required
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
                :disabled="saving || categoriasGasto.length === 0"
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
