import axios from 'axios'

// Cliente sin interceptores, usado solo por el store de auth para
// login/refresh/me. Mantenerlo separado de `axios.js` evita una
// dependencia circular (axios.js -> store/auth -> axios.js) y evita que
// un token viejo o un reintento de refresh se mezclen con el flujo de auth.
const authClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default authClient
