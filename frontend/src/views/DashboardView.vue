<script setup>
import { ArcElement, Chart, DoughnutController, Legend, Tooltip } from 'chart.js'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { getGastosPorCategoria, getResumen } from '../api/dashboard'
import { formatMonto } from '../utils/format'

Chart.register(ArcElement, DoughnutController, Tooltip, Legend)

const MESES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

const PALETA = [
  '#fca311',
  '#e63946',
  '#2a9d8f',
  '#457b9d',
  '#8338ec',
  '#ffb703',
  '#06d6a0',
  '#f72585',
]

const hoy = new Date()
const mes = ref(hoy.getMonth() + 1)
const anio = ref(hoy.getFullYear())

const aniosDisponibles = computed(() => {
  const actual = hoy.getFullYear()
  const anios = []
  for (let a = actual - 3; a <= actual + 1; a++) anios.push(a)
  return anios
})

const loading = ref(true)
const error = ref('')

const resumen = ref(null)
const gastosPorCategoria = ref([])

const balanceClass = computed(() => {
  const balance = Number(resumen.value?.balance ?? 0)
  return balance >= 0 ? 'text-success' : 'text-danger'
})

const canvasRef = ref(null)
let chartInstance = null

async function cargarDashboard() {
  loading.value = true
  error.value = ''
  try {
    const [resumenRes, gastosRes] = await Promise.all([
      getResumen(mes.value, anio.value),
      getGastosPorCategoria(mes.value, anio.value),
    ])
    resumen.value = resumenRes.data
    gastosPorCategoria.value = gastosRes.data.categorias
  } catch {
    error.value = 'No se pudo cargar el dashboard. Reintentá más tarde.'
    resumen.value = null
    gastosPorCategoria.value = []
  } finally {
    loading.value = false
  }

  destruirChart()
  if (gastosPorCategoria.value.length > 0) {
    await nextTick()
    crearChart()
  }
}

function destruirChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

function crearChart() {
  if (!canvasRef.value) return

  const datos = gastosPorCategoria.value
  const labels = datos.map((c) => c.categoria_nombre)
  const valores = datos.map((c) => Number(c.monto))
  const colores = labels.map((_, i) => PALETA[i % PALETA.length])

  chartInstance = new Chart(canvasRef.value, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: valores, backgroundColor: colores, borderWidth: 0 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label(context) {
              const item = datos[context.dataIndex]
              return `${item.categoria_nombre}: ${formatMonto(item.monto)} (${item.porcentaje}%)`
            },
          },
        },
      },
    },
  })
}

onMounted(cargarDashboard)
onBeforeUnmount(destruirChart)
</script>

<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h1 class="h3 mb-1">Resumen financiero</h1>
        <p class="text-muted mb-0">Tu situación financiera del período seleccionado.</p>
      </div>
      <div class="d-flex gap-2">
        <select
          v-model.number="mes"
          class="form-select form-select-sm w-auto"
          aria-label="Mes"
          @change="cargarDashboard"
        >
          <option v-for="(nombre, index) in MESES" :key="nombre" :value="index + 1">
            {{ nombre }}
          </option>
        </select>
        <select
          v-model.number="anio"
          class="form-select form-select-sm w-auto"
          aria-label="Año"
          @change="cargarDashboard"
        >
          <option v-for="a in aniosDisponibles" :key="a" :value="a">{{ a }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="p-5 text-center text-muted">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      Cargando dashboard...
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-12 col-md-4">
          <div class="card shadow-sm border-0 h-100 kpi-card kpi-card--ingresos">
            <div class="card-body">
              <div class="text-muted small mb-1">↑ Ingresos totales</div>
              <div class="h3 mb-0 text-success">{{ formatMonto(resumen?.ingresos ?? 0) }}</div>
            </div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div class="card shadow-sm border-0 h-100 kpi-card kpi-card--gastos">
            <div class="card-body">
              <div class="text-muted small mb-1">↓ Gastos totales</div>
              <div class="h3 mb-0 text-danger">{{ formatMonto(resumen?.gastos ?? 0) }}</div>
            </div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div
            class="card shadow-sm border-0 h-100 kpi-card"
            :class="balanceClass === 'text-success' ? 'kpi-card--ingresos' : 'kpi-card--gastos'"
          >
            <div class="card-body">
              <div class="text-muted small mb-1">= Balance disponible</div>
              <div class="h3 mb-0" :class="balanceClass">
                {{ formatMonto(resumen?.balance ?? 0) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card shadow-sm border-0">
        <div class="card-body">
          <h2 class="h5 mb-3">Gastos por categoría</h2>

          <div v-if="gastosPorCategoria.length === 0" class="text-center text-muted py-5">
            No hay gastos registrados en este período.
          </div>
          <div v-else class="chart-wrapper">
            <canvas ref="canvasRef"></canvas>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.kpi-card {
  border-left: 3px solid transparent;
}

.kpi-card--ingresos {
  border-left-color: #198754;
}

.kpi-card--gastos {
  border-left-color: #dc3545;
}

.chart-wrapper {
  position: relative;
  height: 320px;
}
</style>
