// ─── Auth ────────────────────────────────────────────────────────────────

export type UserRole = 'admin' | 'user' | string

export interface User {
  id: string
  email: string
  full_name: string | null
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}

// ─── Documents ───────────────────────────────────────────────────────────

export type DocumentStatus = 'uploaded' | 'processing' | 'completed' | 'failed'

export type DocumentSource = 'native_pdf' | 'scanned_ocr' | 'image_ocr' | 'unknown'

export type DocType =
  | 'resume'
  | 'invoice'
  | 'contract'
  | 'medical_form'
  | 'business_report'
  | 'unknown'
  | string

export interface DocumentResponse {
  id: string
  filename: string
  content_type: string
  size_bytes: number
  doc_type: DocType
  status: DocumentStatus
  source: DocumentSource
  ocr_confidence: number | null
  page_count: number | null
  processing_ms: number | null
  error_message: string | null
  created_at: string
}

export interface DocumentListResponse {
  items: DocumentResponse[]
  total: number
}

// ─── Extraction ──────────────────────────────────────────────────────────

export interface ResumeEducation {
  institution: string | null
  degree: string | null
  field_of_study: string | null
  start_year: string | number | null
  end_year: string | number | null
}

export interface ResumeExperience {
  company: string | null
  title: string | null
  start_date: string | null
  end_date: string | null
  summary: string | null
}

export interface ResumeData {
  name: string | null
  email: string | null
  phone: string | null
  location: string | null
  summary: string | null
  skills: string[]
  education: ResumeEducation[]
  experience: ResumeExperience[]
}

export interface InvoiceLineItem {
  description: string | null
  quantity: number | null
  unit_price: number | null
  amount: number | null
}

export interface InvoiceData {
  invoice_number: string | null
  issue_date: string | null
  due_date: string | null
  vendor_name: string | null
  vendor_address: string | null
  bill_to: string | null
  currency: string | null
  subtotal: number | null
  tax: number | null
  total: number | null
  line_items: InvoiceLineItem[]
}

// Extraction data is doc-type dependent; resume and invoice are fully-typed.
export type ExtractionData = ResumeData | InvoiceData | Record<string, unknown>

export interface Extraction {
  id: string
  document_id: string
  data: ExtractionData
  missing_fields: string[]
  model: string
  confidence: number | null
  created_at: string
}

export interface DocumentDetailResponse extends DocumentResponse {
  extracted_text: string | null
  extraction: Extraction | null
}

export interface DocumentListParams {
  status?: DocumentStatus
  limit?: number
  offset?: number
}

export interface UploadDocumentParams {
  file: File
  doc_type: string
  process_now: boolean
}
