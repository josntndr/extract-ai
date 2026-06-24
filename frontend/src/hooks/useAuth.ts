import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import type { LoginRequest, RegisterRequest } from '@/types'

/** Whether the user currently has an access token. */
export function useIsAuthenticated(): boolean {
  return useAuthStore((s) => Boolean(s.accessToken))
}

/** Fetch and cache the current user; only runs when authenticated. */
export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const setUser = useAuthStore((s) => s.setUser)

  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const user = await authApi.me()
      setUser(user)
      return user
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000,
  })
}

export function useLogin() {
  const setTokens = useAuthStore((s) => s.setTokens)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (body: LoginRequest) => authApi.login(body),
    onSuccess: async (tokens) => {
      setTokens(tokens)
      await queryClient.invalidateQueries({ queryKey: ['me'] })
      navigate('/', { replace: true })
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (body: RegisterRequest) => authApi.register(body),
    onSuccess: () => {
      navigate('/login', { replace: true })
    },
  })
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clear)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async () => {
      const token = useAuthStore.getState().refreshToken
      if (token) {
        // Best-effort: ignore server errors so logout always proceeds.
        try {
          await authApi.logout(token)
        } catch {
          /* noop */
        }
      }
    },
    onSettled: () => {
      clear()
      queryClient.clear()
      navigate('/login', { replace: true })
    },
  })
}
