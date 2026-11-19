import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { getErrorMessage } from '../api/client'
import {
  deleteDocument,
  getChecklist,
  getDeal,
  getDocuments,
  updateDeal,
  uploadDocuments,
} from '../api/deals'

export default function DealDetail() {
  const { dealId } = useParams()
  const id = Number(dealId)
  const enabled = Number.isFinite(id) && id > 0
  const queryClient = useQueryClient()
  const [uploadError, setUploadError] = useState('')

  const dealQuery = useQuery({
    queryKey: ['deal', id],
    queryFn: () => getDeal(id),
    enabled,
  })
  const documentsQuery = useQuery({
    queryKey: ['documents', id],
    queryFn: () => getDocuments(id),
    enabled,
  })
  const checklistQuery = useQuery({
    queryKey: ['checklist', id],
    queryFn: () => getChecklist(id),
    enabled,
  })

  function refreshDealData(): void {
    queryClient.invalidateQueries({ queryKey: ['documents', id] })
    queryClient.invalidateQueries({ queryKey: ['checklist', id] })
  }

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => uploadDocuments(id, files),
    onSuccess: () => {
      refreshDealData()
      setUploadError('')
    },
    onError: (error: unknown) => setUploadError(getErrorMessage(error)),
  })

  const deleteDocMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: refreshDealData,
  })

  const statusMutation = useMutation({
    mutationFn: () => updateDeal(id, { status: 'complete' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deal', id] })
      queryClient.invalidateQueries({ queryKey: ['deals'] })
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
    },
    onDrop: (files: File[]) => {
      if (files.length > 0) {
        uploadMutation.mutate(files)
      }
    },
  })

  if (!enabled) {
    return <p className="text-red-600">Неверный номер сделки.</p>
  }

  if (dealQuery.isLoading) {
    return <p className="text-slate-600">Загрузка сделки…</p>
  }

  if (dealQuery.isError) {
    return <p className="text-red-600">{getErrorMessage(dealQuery.error)}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <Link to="/deals" className="text-sm text-blue-600 hover:underline">
          ← К списку сделок
        </Link>
        <div className="mt-2 flex items-center justify-between gap-4">
          <h1 className="text-2xl font-semibold">{dealQuery.data?.title}</h1>
          <span className="rounded bg-slate-200 px-2 py-1 text-xs text-slate-700">
            {dealQuery.data?.status === 'open' ? 'Открыта' : 'Завершена'}
          </span>
        </div>
        {dealQuery.data?.description && (
          <p className="mt-2 text-slate-600">{dealQuery.data.description}</p>
        )}
        {dealQuery.data?.status === 'open' && (
          <button
            type="button"
            onClick={() => statusMutation.mutate()}
            disabled={statusMutation.isPending}
            className="mt-3 rounded border border-slate-300 px-3 py-1 text-sm text-slate-700 disabled:opacity-50"
          >
            Отметить завершённой
          </button>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Загрузка документов</h2>
        <div
          {...getRootProps()}
          className="mt-3 cursor-pointer rounded-lg border-2 border-dashed border-slate-300 p-8 text-center text-slate-600 hover:border-blue-500"
        >
          <input {...getInputProps()} />
          {isDragActive
            ? 'Отпустите файлы здесь'
            : 'Перетащите JPG, PNG или PDF сюда либо нажмите для выбора'}
        </div>
        {uploadMutation.isPending && (
          <p className="mt-2 text-sm text-slate-600">Распознаём документы…</p>
        )}
        {uploadError && <p className="mt-2 text-sm text-red-600">{uploadError}</p>}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Чек-лист комплектности</h2>
        {checklistQuery.isLoading && (
          <p className="mt-2 text-slate-600">Проверяем…</p>
        )}
        {checklistQuery.isError && (
          <p className="mt-2 text-red-600">
            {getErrorMessage(checklistQuery.error)}
          </p>
        )}
        {checklistQuery.data && (
          <ul className="mt-3 space-y-1">
            {checklistQuery.data.present.map((name) => (
              <li key={name}>✅ {name}</li>
            ))}
            {checklistQuery.data.missing.map((name) => (
              <li key={name}>❌ {name}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Документы</h2>
        {documentsQuery.isLoading && (
          <p className="mt-2 text-slate-600">Загрузка…</p>
        )}
        {documentsQuery.data?.length === 0 && (
          <p className="mt-2 text-slate-600">Документов пока нет.</p>
        )}
        <ul className="mt-3 space-y-2">
          {documentsQuery.data?.map((document) => (
            <li
              key={document.id}
              className="flex items-center justify-between gap-4 rounded border border-slate-200 px-3 py-2"
            >
              <div>
                <p className="font-medium">{document.filename}</p>
                <p className="text-sm text-slate-600">
                  {document.doc_type ?? 'Не определен'}
                  {document.confidence !== null &&
                    ` · уверенность ${Math.round(document.confidence * 100)}%`}
                </p>
              </div>
              <button
                type="button"
                onClick={() => deleteDocMutation.mutate(document.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Удалить
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
