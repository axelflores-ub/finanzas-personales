<script setup>
import { computed } from 'vue'

import { claseUtilizacion, formatMonto } from '../../utils/format'

const props = defineProps({
  presupuesto: { type: Object, required: true },
})

defineEmits(['editar', 'eliminar'])

const clase = computed(() => claseUtilizacion(props.presupuesto.porcentaje_utilizado))
const anchoBarra = computed(() =>
  Math.min(Number(props.presupuesto.porcentaje_utilizado), 100),
)
const restanteEsNegativo = computed(() => Number(props.presupuesto.restante) < 0)
</script>

<template>
  <div class="card shadow-sm border-0 mb-3">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-2 gap-2">
        <div>
          <div class="fw-semibold">{{ presupuesto.categoria_nombre }}</div>
          <div class="small text-muted">
            {{ formatMonto(presupuesto.gasto_real) }} de {{ formatMonto(presupuesto.monto_limite) }}
          </div>
        </div>
        <span class="badge rounded-pill" :class="`text-bg-${clase}`">
          {{ presupuesto.porcentaje_utilizado }}%
        </span>
      </div>

      <div class="progress mb-2" style="height: 8px">
        <div class="progress-bar" :class="`bg-${clase}`" :style="{ width: anchoBarra + '%' }"></div>
      </div>

      <div class="d-flex justify-content-between align-items-center">
        <div class="small" :class="restanteEsNegativo ? 'text-danger' : 'text-muted'">
          {{ restanteEsNegativo ? 'Excedido en' : 'Disponible' }}:
          {{ formatMonto(Math.abs(Number(presupuesto.restante))) }}
        </div>
        <div>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary me-2"
            @click="$emit('editar', presupuesto)"
          >
            Editar
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-danger"
            @click="$emit('eliminar', presupuesto)"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
