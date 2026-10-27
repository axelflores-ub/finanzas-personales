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

    <main class="app-main">
      <div class="app-main-inner">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-sidebar {
  background: var(--color-ink-900);
  color: #fff;
  padding: 1.5rem 1rem;
  display: flex;
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
  flex-direction: row;
  gap: 0.25rem;
  overflow-x: auto;
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
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
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
  max-width: 120px;
}

.sidebar-user .btn {
  width: auto;
  white-space: nowrap;
}

.app-main {
  flex: 1;
  background: var(--color-bg);
  padding: var(--space-6);
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
    width: 240px;
    flex-shrink: 0;
    flex-direction: column;
    align-items: stretch;
  }

  .sidebar-nav {
    flex-direction: column;
  }

  .sidebar-user {
    flex-direction: column;
    align-items: stretch;
    margin-left: 0;
    margin-top: auto;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 1rem;
  }

  .user-name {
    max-width: none;
  }

  .app-main {
    padding: var(--space-12);
  }
}
</style>
