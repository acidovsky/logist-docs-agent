import { client } from './client'
import type { Checklist, Deal, DealStatus, DocumentItem } from './types'

// Поля для создания сделки.
export interface DealCreate {
  title: string
  description?: string
}

// Поля для частичного обновления сделки.
export interface DealUpdate {
  title?: string
  description?: string
  status?: DealStatus
}

// Список сделок текущего пользователя.
export async function getDeals(): Promise<Deal[]> {
  const response = await client.get<Deal[]>('/deals')
  return response.data
}

// Создание сделки.
export async function createDeal(input: DealCreate): Promise<Deal> {
  const response = await client.post<Deal>('/deals', input)
  return response.data
}

// Детали сделки.
export async function getDeal(dealId: number): Promise<Deal> {
  const response = await client.get<Deal>(`/deals/${dealId}`)
  return response.data
}

// Частичное обновление сделки.
export async function updateDeal(dealId: number, input: DealUpdate): Promise<Deal> {
  const response = await client.patch<Deal>(`/deals/${dealId}`, input)
  return response.data
}

// Удаление сделки.
export async function deleteDeal(dealId: number): Promise<void> {
  await client.delete(`/deals/${dealId}`)
}

// Документы сделки.
export async function getDocuments(dealId: number): Promise<DocumentItem[]> {
  const response = await client.get<DocumentItem[]>(`/deals/${dealId}/documents`)
  return response.data
}

// Чек-лист комплектности.
export async function getChecklist(dealId: number): Promise<Checklist> {
  const response = await client.get<Checklist>(`/deals/${dealId}/checklist`)
  return response.data
}

// Загрузка нескольких файлов в сделку.
export async function uploadDocuments(
  dealId: number,
  files: File[],
): Promise<DocumentItem[]> {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  const response = await client.post<DocumentItem[]>(
    `/deals/${dealId}/documents`,
    formData,
  )
  return response.data
}

// Удаление документа.
export async function deleteDocument(documentId: number): Promise<void> {
  await client.delete(`/documents/${documentId}`)
}
