import { client } from './client'
import type { Token, User } from './types'

// Регистрация нового пользователя.
export async function register(email: string, password: string): Promise<User> {
  const response = await client.post<User>('/auth/register', { email, password })
  return response.data
}

// Вход и получение токена доступа.
export async function login(email: string, password: string): Promise<Token> {
  const response = await client.post<Token>('/auth/login', { email, password })
  return response.data
}

// Данные текущего пользователя.
export async function getCurrentUser(): Promise<User> {
  const response = await client.get<User>('/auth/me')
  return response.data
}
