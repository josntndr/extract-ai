import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { documentsApi } from '@/services/api'
import type {
  DocumentDetailResponse,
  DocumentListParams,
  DocumentListResponse,
  UploadDocumentParams,
} from '@/types'

const PENDING_STATUSES = new Set(['uploaded', 'processing'])

export const documentKeys = {
  all: ['documents'] as const,
  list: (params: DocumentListParams) =>
    [...documentKeys.all, 'list', params] as const,
  detail: (id: string) => [...documentKeys.all, 'detail', id] as const,
}

/**
 * List the current user's documents. Polls every 4s while any document is
 * still in an "uploaded" or "processing" state so the UI tracks the pipeline.
 */
export function useDocuments(params: DocumentListParams = {}) {
  return useQuery({
    queryKey: documentKeys.list(params),
    queryFn: () => documentsApi.list(params),
    refetchInterval: (query) => {
      const data = query.state.data as DocumentListResponse | undefined
      const hasPending = data?.items.some((d) => PENDING_STATUSES.has(d.status))
      return hasPending ? 4000 : false
    },
  })
}

/**
 * Fetch a single document's detail. Polls every 4s while it is still pending.
 */
export function useDocument(id: string | undefined) {
  return useQuery({
    queryKey: documentKeys.detail(id ?? ''),
    queryFn: () => documentsApi.get(id as string),
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const data = query.state.data as DocumentDetailResponse | undefined
      return data && PENDING_STATUSES.has(data.status) ? 4000 : false
    },
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (params: UploadDocumentParams) => documentsApi.upload(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.all })
    },
  })
}

export function useReprocessDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => documentsApi.reprocess(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: documentKeys.all })
    },
  })
}

export function useDeleteDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => documentsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.all })
    },
  })
}
