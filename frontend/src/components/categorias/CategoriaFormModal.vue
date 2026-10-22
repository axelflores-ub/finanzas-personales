<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  categoria: { type: Object, default: null }, // null = crear, objeto = editar
  saving: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const nombre = ref('')
const tipo = ref('GASTO')

watch(
  () => props.show,
  (isOpen) => {
    if (isOpen) {
      nombre.value = props.categoria?.nombre ?? ''
      tipo.value = props.categoria?.tipo ?? 'GASTO'
    }
  },
  { immediate: true },
)

function handleSubmit() {
  emit('submit', { nombre: nombre.value.trim(), tipo: tipo.value })
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
                {{ categoria ? 'Editar categoría' : 'Nueva categoría' }}
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
                <label class="form-label" for="categoria-nombre">Nombre</label>
                <input
                  id="categoria-nombre"
                  v-model="nombre"
                  type="text"
                  class="form-control"
                  maxlength="100"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label" for="categoria-tipo">Tipo</label>
                <select id="categoria-tipo" v-model="tipo" class="form-select">
                  <option value="INGRESO">Ingreso</option>
                  <option value="GASTO">Gasto</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="emit('cancel')">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
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
