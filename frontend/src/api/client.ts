import axios from 'axios'

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
const isLocalApiBaseUrl =
  configuredApiBaseUrl?.includes('localhost') || configuredApiBaseUrl?.includes('127.0.0.1')
const apiBaseUrl =
  import.meta.env.PROD && isLocalApiBaseUrl
    ? window.location.origin
    : configuredApiBaseUrl || window.location.origin

const client = axios.create({
  baseURL: `${apiBaseUrl}/api`,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      const path = window.location.pathname
      if (path !== '/' && path !== '/auth') {
        window.location.href = '/auth'
      }
    }
    return Promise.reject(error)
  },
)

export default client
