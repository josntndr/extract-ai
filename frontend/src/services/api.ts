import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'
import { authStore } from '@/store/auth'
import type {
  DocumentDetailResponse,
  DocumentListParams,
  DocumentListResponse,
  DocumentResponse,
  LoginRequest,
  RegisterRequest,
  TokenPair,
  UploadDocumentParams,
  User,
} from '@/types'

export const API_URL =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Request interceptor: attach bearer token ────────────────────────────

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = authStore.getState().accessToken
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

// ─── Response interceptor: refresh-on-401 (once) ─────────────────────────

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// De-dupe concurrent refreshes so multiple 401s share one refresh call.
let refreshPromise: Promise<TokenPair> | null = null

async function performRefresh(): Promise<TokenPair> {
  const refreshToken = authStore.getState().refreshToken
  if (!refreshToken) throw new Error('No refresh token available')

  // Use a bare axios call to avoid recursive interceptors.
  const { data } = await axios.post<TokenPair>(`${API_URL}/auth/refresh`, {
    refresh_token: refreshToken,
  })
  authStore.getState().setTokens(data)
  return data
}

function forceLogout() {
  authStore.getState().clear()
  if (window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined
    const status = error.response?.status

    const isRefreshCall = original?.url?.includes('/auth/refresh')

    if (status === 401 && original && !original._retry && !isRefreshCall) {
      original._retry = true
      try {
        refreshPromise = refreshPromise ?? performRefresh()
        const tokens = await refreshPromise
        refreshPromise = null
        original.headers.set('Authorization', `Bearer ${tokens.access_token}`)
        return api(original)
      } catch (refreshError) {
        refreshPromise = null
        forceLogout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

// ─── Endpoints ────────────────────────────────────────────────────────────

export const authApi = {
  register: (body: RegisterRequest) =>
    api.post<User>('/auth/register', body).then((r) => r.data),

  login: (body: LoginRequest) =>
    api.post<TokenPair>('/auth/login', body).then((r) => r.data),

  refresh: (refresh_token: string) =>
    api.post<TokenPair>('/auth/refresh', { refresh_token }).then((r) => r.data),

  logout: (refresh_token: string) =>
    api.post<void>('/auth/logout', { refresh_token }).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),
}

export const documentsApi = {
  list: (params: DocumentListParams = {}) =>
    api
      .get<DocumentListResponse>('/documents', { params })
      .then((r) => r.data),

  get: (id: string) =>
    api.get<DocumentDetailResponse>(`/documents/${id}`).then((r) => r.data),

  upload: ({ file, doc_type, process_now }: UploadDocumentParams) => {
    const form = new FormData()
    form.append('file', file)
    form.append('doc_type', doc_type)
    form.append('process_now', process_now ? 'true' : 'false')
    return api
      .post<DocumentResponse>('/documents', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },

  reprocess: (id: string) =>
    api
      .post<DocumentResponse>(`/documents/${id}/reprocess`)
      .then((r) => r.data),

  remove: (id: string) =>
    api.delete<void>(`/documents/${id}`).then((r) => r.data),
}
