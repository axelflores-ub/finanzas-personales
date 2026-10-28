<script setup>
import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  DoughnutController,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import {
  getEvolucionMensual,
  getGastosPorCategoria,
  getPresupuestosResumen,
  getResumen,
} from '../api/dashboard'
import { MESES, MESES_CORTOS, aniosDisponibles, claseUtilizacion, formatMonto } from '../utils/format'

Chart.register(
  ArcElement,
  DoughnutController,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
)

// Paleta de categorías del gráfico de dona: distinguible entre sí, en línea
// con el sistema de diseño (Etapa 8C). No reutiliza los tonos semánticos de
// ingreso/gasto (verde/rojo) porque todas las porciones de este gráfico son
// gastos — el color acá solo diferencia categorías, no indica tipo.
const PALETA = [
  '#4f46e5',
  '#0d9488',
  '#d97706',
  '#db2777',
  '#7c3aed',
  '#0ea5e9',
  '#64748b',
  '#b91c1c',
]

const hoy = new Date()
const mes = ref(hoy.getMonth() + 1)
const anio = ref(hoy.getFullYear())

const loading = ref(true)
const error = ref('')

const resumen = ref(null)
const gastosPorCategoria = ref([])
const presupuestosResumen = ref(null)
const evolucionMensual = ref([])

const tieneEvolucion = computed(() =>
  evolucionMensual.value.some((m) => Number(m.ingresos) > 0 || Number(m.gastos) > 0),
)

const balanceClass = computed(() => {
  const balance = Number(resumen.value?.balance ?? 0)
  return balance >= 0 ? 'text-success' : 'text-danger'
})

const canvasRef = ref(null)
let chartInstance = null

const evolucionCanvasRef = ref(null)
let evolucionChartInstance = null

// Id incremental para descartar respuestas obsoletas: si el usuario cambia
// mes/año antes de que vuelva el pedido anterior, esa respuesta ya no
// corresponde al período vigente y no debe pisar el estado ni redibujar los
// gráficos. Cada llamada a cargarDashboard() toma el valor actual; al volver
// de cada `await`, si dashboardRequestId ya avanzó, esta corrida es vieja y
// se aborta sin tocar nada.
let dashboardRequestId = 0

async function cargarDashboard() {
  const requestId = ++dashboardRequestId
  loading.value = true
  error.value = ''

  let resumenRes, gastosRes, presupuestosRes, evolucionRes
  try {
    ;[resumenRes, gastosRes, presupuestosRes, evolucionRes] = await Promise.all([
      getResumen(mes.value, anio.value),
      getGastosPorCategoria(mes.value, anio.value),
      getPresupuestosResumen(mes.value, anio.value),
      getEvolucionMensual(anio.value),
    ])
  } catch {
    if (requestId !== dashboardRequestId) return
    error.value = 'No se pudo cargar el dashboard. Reintentá más tarde.'
    resumen.value = null
    gastosPorCategoria.value = []
    presupuestosResumen.value = null
    evolucionMensual.value = []
    loading.value = false
    return
  }

  if (requestId !== dashboardRequestId) return

  resumen.value = resumenRes.data
  gastosPorCategoria.value = gastosRes.data.categorias
  presupuestosResumen.value = presupuestosRes.data
  evolucionMensual.value = evolucionRes.data.meses
  loading.value = false

  destruirChart()
  if (gastosPorCategoria.value.length > 0) {
    await nextTick()
    if (requestId !== dashboardRequestId) return
    crearChart()
  }

  destruirEvolucionChart()
  if (tieneEvolucion.value) {
    await nextTick()
    if (requestId !== dashboardRequestId) return
    crearEvolucionChart()
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

function destruirEvolucionChart() {
  if (evolucionChartInstance) {
    evolucionChartInstance.destroy()
    evolucionChartInstance = null
  }
}

function crearEvolucionChart() {
  if (!evolucionCanvasRef.value) return

  const datos = evolucionMensual.value
  const ingresos = datos.map((m) => Number(m.ingresos))
  const gastos = datos.map((m) => Number(m.gastos))

  evolucionChartInstance = new Chart(evolucionCanvasRef.value, {
    type: 'bar',
    data: {
      labels: MESES_CORTOS,
      datasets: [
        { label: 'Ingresos', data: ingresos, backgroundColor: '#16a34a' },
        { label: 'Gastos', data: gastos, backgroundColor: '#dc2626' },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$ ${Number(value).toLocaleString('es-AR')}`,
          },
        },
      },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${formatMonto(context.parsed.y)}`,
          },
        },
      },
    },
  })
}

onMounted(cargarDashboard)
onBeforeUnmount(() => {
  destruirChart()
  destruirEvolucionChart()
})
</script>

<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h1 class="page-title mb-1">Resumen financiero</h1>
        <p class="page-subtitle mb-0">Tu situación financiera del período seleccionado.</p>
      </div>
      <div class="d-flex gap-2">
        <select
          v-model.number="mes"
          class="form-select form-select-sm w-auto fp-select"
          aria-label="Mes"
          @change="cargarDashboard"
        >
          <option v-for="(nombre, index) in MESES" :key="nombre" :value="index + 1">
            {{ nombre }}
          </option>
        </select>
        <select
          v-model.number="anio"
          class="form-select form-select-sm w-auto fp-select"
          aria-label="Año"
          @change="cargarDashboard"
        >
          <option v-for="a in aniosDisponibles()" :key="a" :value="a">{{ a }}</option>
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
        <div class="col-12 col-sm-6 col-lg-4">
          <div class="card fp-card h-100">
            <div class="card-body">
              <div class="kpi-label mb-1">↑ Ingresos totales</div>
              <div class="kpi-value text-success">{{ formatMonto(resumen?.ingresos ?? 0) }}</div>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-lg-4">
          <div class="card fp-card h-100">
            <div class="card-body">
              <div class="kpi-label mb-1">↓ Gastos totales</div>
              <div class="kpi-value text-danger">{{ formatMonto(resumen?.gastos ?? 0) }}</div>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-lg-4">
          <div class="card fp-card h-100">
            <div class="card-body">
              <div class="kpi-label mb-1">= Balance disponible</div>
              <div class="kpi-value" :class="balanceClass">
                {{ formatMonto(resumen?.balance ?? 0) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-12 col-lg-5">
          <div class="card fp-card h-100">
            <div class="card-body">
              <h2 class="section-title mb-3">Gastos por categoría</h2>

              <div v-if="gastosPorCategoria.length === 0" class="text-center text-muted py-5">
                No hay gastos registrados en este período.
              </div>
              <div v-else class="chart-wrapper">
                <canvas ref="canvasRef"></canvas>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-lg-7">
          <div class="card fp-card h-100">
            <div class="card-body">
              <h2 class="section-title mb-3">Evolución mensual · {{ anio }}</h2>

              <div v-if="!tieneEvolucion" class="text-center text-muted py-5">
                No hay movimientos registrados en {{ anio }}.
              </div>
              <div v-else class="chart-wrapper">
                <canvas ref="evolucionCanvasRef"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card fp-card mt-4">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h2 class="section-title mb-0">Presupuestos del período</h2>
            <router-link :to="{ name: 'presupuestos' }" class="small">Ver detalle →</router-link>
          </div>

          <div
            v-if="!presupuestosResumen || presupuestosResumen.presupuesto_total === '0.00'"
            class="text-center text-muted py-4"
          >
            No definiste presupuestos para este período.
            <router-link :to="{ name: 'presupuestos' }">Creá uno</router-link>.
          </div>
          <div v-else>
            <div class="row g-3 mb-3 text-center text-md-start">
              <div class="col-12 col-md-4">
                <div class="mini-label">Presupuesto total</div>
                <div class="mini-value">{{ formatMonto(presupuestosResumen.presupuesto_total) }}</div>
              </div>
              <div class="col-12 col-md-4">
                <div class="mini-label">Gasto real</div>
                <div class="mini-value">
                  {{ formatMonto(presupuestosResumen.gasto_real_presupuestado) }}
                </div>
              </div>
              <div class="col-12 col-md-4">
                <div class="mini-label">Utilizado</div>
                <div class="mini-value">{{ presupuestosResumen.porcentaje_utilizado }}%</div>
              </div>
            </div>
            <div class="progress fp-progress" style="height: 8px">
              <div
                class="progress-bar"
                :class="`bg-${claseUtilizacion(presupuestosResumen.porcentaje_utilizado)}`"
                :style="{
                  width: Math.min(Number(presupuestosResumen.porcentaje_utilizado), 100) + '%',
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-title {
  font-size: var(--font-size-xl);
  margin: 0;
}

.page-subtitle {
  color: var(--color-ink-500);
  font-size: var(--font-size-sm);
}

.section-title {
  font-size: var(--font-size-lg);
  margin: 0;
}

.kpi-label {
  color: var(--color-ink-500);
  font-size: var(--font-size-xs);
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.kpi-value {
  font-size: clamp(1.15rem, 4vw, 1.5rem);
  font-weight: 700;
  white-space: nowrap;
}

.mini-label {
  color: var(--color-ink-500);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.mini-value {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin-top: 0.15rem;
}

.fp-select {
  border-radius: var(--radius-sm);
}

.fp-progress {
  background: var(--color-border);
  border-radius: 999px;
  overflow: hidden;
}

.chart-wrapper {
  position: relative;
  height: 320px;
}

/*
 * Colores semánticos exactos del sistema (Etapa 8C): las utilidades de
 * Bootstrap text-success/text-danger/bg-success/bg-warning/bg-danger traen
 * su propio verde/amarillo/rojo por defecto. Se redeclaran acá, con alcance
 * scoped (solo afecta a este componente, no a Categorías/Presupuestos, que
 * todavía no pasaron por su propia etapa de rediseño).
 */
.text-success {
  color: var(--color-success) !important;
}

.text-danger {
  color: var(--color-danger) !important;
}

.bg-success {
  background-color: var(--color-success) !important;
}

.bg-warning {
  background-color: var(--color-warning) !important;
}

.bg-danger {
  background-color: var(--color-danger) !important;
}

.alert-danger {
  background-color: var(--color-danger-soft);
  border-color: var(--color-danger-soft);
  color: var(--color-danger);
}
</style>
