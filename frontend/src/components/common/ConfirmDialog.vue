<script setup>
import { computed, ref } from 'vue'

import { useModalA11y } from '../../composables/useModalA11y'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar' },
  message: { type: String, default: '¿Confirmás esta acción?' },
  confirmLabel: { type: String, default: 'Confirmar' },
  confirmVariant: { type: String, default: 'danger' },
})

const emit = defineEmits(['confirm', 'cancel'])

const modalRef = ref(null)
useModalA11y(
  computed(() => props.show),
  modalRef,
  () => emit('cancel'),
)

// 'danger' usa la variante suave del sistema (misma que Eliminar en las
// tablas); cualquier otra variante cae en la clase sólida de Bootstrap.
const confirmButtonClass = computed(() =>
  props.confirmVariant === 'danger' ? 'fp-btn-danger-soft' : `btn-${props.confirmVariant}`,
)
</script>

<template>
  <div v-if="show" class="fp-modal-backdrop" @click.self="emit('cancel')">
    <div ref="modalRef" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ title }}</h5>
            <button
              type="button"
              class="btn-close"
              aria-label="Cerrar"
              @click="emit('cancel')"
            ></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">{{ message }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn fp-btn-outline" @click="emit('cancel')">
              Cancelar
            </button>
            <button type="button" class="btn" :class="confirmButtonClass" @click="emit('confirm')">
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
