// Общие типы данных приложения.

export interface User {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export type DealStatus = 'open' | 'complete'

export interface Deal {
  id: number
  title: string
  description: string | null
  status: DealStatus
  owner_id: number
  created_at: string
  updated_at: string
}

export interface DocumentItem {
  id: number
  deal_id: number
  doc_type: string | null
  filename: string
  file_path: string
  ocr_text: string | null
  confidence: number | null
  uploaded_at: string
}

export interface Checklist {
  present: string[]
  missing: string[]
}
