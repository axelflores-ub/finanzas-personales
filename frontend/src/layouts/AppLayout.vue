<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <!-- Sidebar: solo desktop (>=768px), oculta en mobile vía CSS. -->
    <aside class="app-sidebar">
      <div class="sidebar-brand">
        <span class="brand-mark">$</span>
        <span class="brand-name">Finanzas Personales</span>
      </div>

      <nav class="sidebar-nav">
        <router-link class="nav-link" active-class="active" :to="{ name: 'dashboard' }">
          Dashboard
        </router-link>
        <router-link class="nav-link" active-class="active" :to="{ name: 'categorias' }">
          Categorías
        </router-link>
        <router-link class="nav-link" active-class="active" :to="{ name: 'movimientos' }">
          Movimientos
        </router-link>
        <router-link class="nav-link" active-class="active" :to="{ name: 'presupuestos' }">
          Presupuestos
        </router-link>
      </nav>

      <div class="sidebar-user">
        <div class="user-info">
          <div class="user-avatar">{{ authStore.user?.username?.[0]?.toUpperCase() }}</div>
          <div class="user-name text-truncate">{{ authStore.user?.username }}</div>
        </div>
        <button type="button" class="btn btn-sm btn-outline-light w-100" @click="handleLogout">
          Cerrar sesión
        </button>
      </div>
    </aside>

    <!-- Barra superior: solo mobile (<768px), oculta en desktop vía CSS. -->
    <header class="mobile-topbar">
      <div class="sidebar-brand">
        <span class="brand-mark">$</span>
        <span class="brand-name">Finanzas Personales</span>
      </div>
      <div class="mobile-topbar-user">
        <div class="user-avatar">{{ authStore.user?.username?.[0]?.toUpperCase() }}</div>
        <button
          type="button"
          class="mobile-logout-btn"
          aria-label="Cerrar sesión"
          @click="handleLogout"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </header>

    <main class="app-main">
      <div class="app-main-inner">
        <router-view />
      </div>
    </main>

    <!-- Barra de pestañas inferior: solo mobile (<768px). Reemplaza la fila
         horizontal con scroll que no avisaba que había más opciones fuera
         de pantalla (hallazgo de la Etapa 8A) — acá los 4 ítems están
         siempre visibles a la vez, sin scroll. -->
    <nav class="mobile-tabbar" aria-label="Navegación principal">
      <router-link class="tab-link" active-class="active" :to="{ name: 'dashboard' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        <span>Dashboard</span>
      </router-link>
      <router-link class="tab-link" active-class="active" :to="{ name: 'categorias' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20.59 13.41 11 3.83A2 2 0 0 0 9.58 3.25L4 3a1 1 0 0 0-1 1l.25 5.58a2 2 0 0 0 .58 1.42l9.59 9.59a2 2 0 0 0 2.83 0l4.34-4.34a2 2 0 0 0 0-2.84Z" />
          <circle cx="7.5" cy="7.5" r="1.5" />
        </svg>
        <span>Categorías</span>
      </router-link>
      <router-link class="tab-link" active-class="active" :to="{ name: 'movimientos' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="8" y1="6" x2="21" y2="6" />
          <line x1="8" y1="12" x2="21" y2="12" />
          <line x1="8" y1="18" x2="21" y2="18" />
          <line x1="3" y1="6" x2="3.01" y2="6" />
          <line x1="3" y1="12" x2="3.01" y2="12" />
          <line x1="3" y1="18" x2="3.01" y2="18" />
        </svg>
        <span>Movimientos</span>
      </router-link>
      <router-link class="tab-link" active-class="active" :to="{ name: 'presupuestos' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <circle cx="12" cy="12" r="5.5" />
          <circle cx="12" cy="12" r="2" />
        </svg>
        <span>Presupuestos</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Oculta por defecto: en mobile (<768px) la navegación es la barra
   superior + la barra de pestañas inferior de más abajo. */
.app-sidebar {
  display: none;
  background: var(--color-ink-900);
  color: #fff;
  padding: 1.5rem 1rem;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 600;
  font-size: 1.05rem;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  font-weight: 700;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-nav .nav-link {
  color: rgba(255, 255, 255, 0.75);
  padding: 0.5rem 0.9rem;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  font-size: 0.9rem;
}

.sidebar-nav .nav-link.active {
  background: rgba(79, 70, 229, 0.25);
  color: #a5b4fc;
  font-weight: 600;
}

.sidebar-user {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-size: 0.85rem;
}

.sidebar-user .btn {
  width: auto;
  white-space: nowrap;
}

/* Barra superior (mobile) */
.mobile-topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--color-ink-900);
  color: #fff;
  padding: 0.85rem 1rem;
  padding-top: calc(0.85rem + env(safe-area-inset-top, 0px));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.mobile-topbar-user {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.mobile-logout-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: transparent;
  color: #fff;
}
.mobile-logout-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* Barra de pestañas inferior (mobile): reemplaza la fila horizontal con
   scroll que no avisaba que había más opciones fuera de pantalla
   (hallazgo de la Etapa 8A) — los 4 ítems quedan siempre visibles a la
   vez, sin necesidad de scrollear para encontrar "Presupuestos". */
.mobile-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: flex;
  background: var(--color-ink-900);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.mobile-tabbar .tab-link {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  padding: 0.5rem 0.25rem 0.6rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.68rem;
  font-weight: 600;
  text-align: center;
}

.mobile-tabbar .tab-link span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.mobile-tabbar .tab-link.active {
  color: #a5b4fc;
}

.app-main {
  flex: 1;
  min-width: 0; /* por defecto un hijo flex no se achica más que su contenido
                   (ej. una tabla ancha) y fuerza scroll horizontal de toda
                   la página; esto lo deja encogerse y que .table-responsive
                   contenga su propio scroll en vez de desbordar el layout */
  background: var(--color-bg);
  padding: var(--space-6);
  /* Espacio para que el contenido no quede tapado por la barra de
     pestañas fija de abajo (altura real de la barra + safe-area). */
  padding-bottom: calc(var(--space-6) + 68px + env(safe-area-inset-bottom, 0px));
}

.app-main-inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  width: 100%;
}

@media (min-width: 768px) {
  .app-shell {
    flex-direction: row;
  }

  .app-sidebar {
    display: flex;
    width: 240px;
    flex-shrink: 0;
    align-items: stretch;
  }

  .mobile-topbar,
  .mobile-tabbar {
    display: none;
  }

  .app-main {
    padding: var(--space-12);
  }
}
</style>
