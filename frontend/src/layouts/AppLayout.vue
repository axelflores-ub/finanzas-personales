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
        <router-link class="nav-link" active-class="active" :to="{ name: 'categorias' }">
          Categorías
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
      <router-view />
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
  background: #14213d;
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
  border-radius: 8px;
  background: #fca311;
  color: #14213d;
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
  border-radius: 8px;
  white-space: nowrap;
  font-size: 0.9rem;
}

.sidebar-nav .nav-link.active {
  background: rgba(252, 163, 17, 0.15);
  color: #fca311;
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
  background: #f5f7fb;
  padding: 1.5rem;
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
    padding: 2.5rem;
  }
}
</style>
