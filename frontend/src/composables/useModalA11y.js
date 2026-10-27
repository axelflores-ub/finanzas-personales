import { nextTick, onBeforeUnmount, watch } from 'vue'

const SELECTOR_FOCOABLES =
  'a[href], button:not([disabled]), textarea:not([disabled]), ' +
  'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

/**
 * Accesibilidad de teclado básica para los modales custom del proyecto
 * (los que arman su propio overlay con `v-if` en vez de usar el JS de
 * Bootstrap — ver CLAUDE.md). Da, sin ninguna librería nueva:
 *
 * - Cierre con Escape.
 * - Foco inicial dentro del modal al abrirse.
 * - Foco atrapado con Tab/Shift+Tab mientras está abierto.
 * - Restauración del foco al elemento que lo abrió, al cerrarse.
 *
 * @param {import('vue').Ref<boolean> | import('vue').ComputedRef<boolean>} showRef
 * @param {import('vue').Ref<HTMLElement | null>} containerRef - ref al
 *   elemento con `role="dialog"` (debe tener `tabindex="-1"` como fallback
 *   de foco si el modal no tuviera ningún campo/botón focoable).
 * @param {() => void} onClose - se invoca al presionar Escape.
 */
export function useModalA11y(showRef, containerRef, onClose) {
  let elementoPrevio = null

  function focoables() {
    const contenedor = containerRef.value
    if (!contenedor) return []
    return Array.from(contenedor.querySelectorAll(SELECTOR_FOCOABLES))
  }

  function manejarTeclado(event) {
    if (event.key === 'Escape') {
      event.stopPropagation()
      onClose()
      return
    }

    if (event.key !== 'Tab') return

    const elementos = focoables()
    if (elementos.length === 0) return

    const primero = elementos[0]
    const ultimo = elementos[elementos.length - 1]

    if (event.shiftKey && document.activeElement === primero) {
      event.preventDefault()
      ultimo.focus()
    } else if (!event.shiftKey && document.activeElement === ultimo) {
      event.preventDefault()
      primero.focus()
    }
  }

  watch(showRef, async (abierto) => {
    if (abierto) {
      elementoPrevio = document.activeElement
      document.addEventListener('keydown', manejarTeclado)
      await nextTick()
      const [primero] = focoables()
      ;(primero ?? containerRef.value)?.focus()
    } else {
      document.removeEventListener('keydown', manejarTeclado)
      elementoPrevio?.focus?.()
      elementoPrevio = null
    }
  })

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', manejarTeclado)
  })
}
