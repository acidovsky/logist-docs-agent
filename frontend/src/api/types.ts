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
