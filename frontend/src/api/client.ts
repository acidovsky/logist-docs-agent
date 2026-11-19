import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

// Ключ токена в локальном хранилище браузера.
export const TOKEN_KEY = 'token'

// Клиент запросов к backend через прокси Vite.
// Заголовок Content-Type не задаём вручную: axios сам выставит JSON для объектов
// и позволит браузеру указать boundary для загрузки файлов.
export const client = axios.create({
  baseURL: '/api',
})

// Прикладываем токен к каждому запросу.
client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Если токен больше не действует, удаляем его.
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    return Promise.reject(error)
  },
)

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

// Достать понятный текст ошибки из ответа backend.
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    return error.message
  }
  return 'Неизвестная ошибка'
}
