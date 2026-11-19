import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getErrorMessage } from '../api/client'
import { createDeal, deleteDeal, getDeals } from '../api/deals'

export default function Deals() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [formError, setFormError] = useState('')

  const dealsQuery = useQuery({ queryKey: ['deals'], queryFn: getDeals })

  const createMutation = useMutation({
    mutationFn: createDeal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deals'] })
      setShowForm(false)
      setTitle('')
      setDescription('')
      setFormError('')
    },
    onError: (error: unknown) => setFormError(getErrorMessage(error)),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDeal,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['deals'] }),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    createMutation.mutate({ title, description })
  }

  if (dealsQuery.isLoading) {
    return <p className="text-slate-600">Загрузка сделок…</p>
  }

  if (dealsQuery.isError) {
    return <p className="text-red-600">{getErrorMessage(dealsQuery.error)}</p>
  }

  return (
    <section>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Сделки</h1>
        <button
          type="button"
          onClick={() => setShowForm(true)}
          className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
        >
          Создать сделку
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mt-4 space-y-4 rounded-lg border border-slate-200 bg-white p-6"
        >
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Название</span>
            <input
              required
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Описание</span>
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            />
          </label>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Создаём…' : 'Создать'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="rounded border border-slate-300 px-4 py-2 text-slate-700"
            >
              Отмена
            </button>
          </div>
        </form>
      )}

      <div className="mt-6 space-y-3">
        {dealsQuery.data?.length === 0 && (
          <p className="text-slate-600">Сделок пока нет.</p>
        )}
        {dealsQuery.data?.map((deal) => (
          <article
            key={deal.id}
            className="rounded-lg border border-slate-200 bg-white p-4"
          >
            <div className="flex items-center justify-between gap-4">
              <Link
                to={`/deals/${deal.id}`}
                className="font-medium text-blue-600 hover:underline"
              >
                {deal.title}
              </Link>
              <span
                className={
                  deal.status === 'open'
                    ? 'rounded bg-amber-100 px-2 py-1 text-xs text-amber-800'
                    : 'rounded bg-green-100 px-2 py-1 text-xs text-green-800'
                }
              >
                {deal.status === 'open' ? 'Открыта' : 'Завершена'}
              </span>
            </div>
            {deal.description && (
              <p className="mt-2 text-sm text-slate-600">{deal.description}</p>
            )}
            <button
              type="button"
              onClick={() => deleteMutation.mutate(deal.id)}
              className="mt-3 text-sm text-red-600 hover:underline"
            >
              Удалить
            </button>
          </article>
        ))}
      </div>
    </section>
  )
}
