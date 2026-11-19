# Logist Docs Agent

Многопользовательский веб-сервис для работы с пакетами логистических документов.

## Структура проекта

- `backend/` — серверная часть на FastAPI, SQLModel и SQLite. Код приложения находится в `backend/app/`, загруженные файлы — в `backend/uploads/`.
- `frontend/` — интерфейс на React и TypeScript, собирается через Vite.
- `legacy/` — исходный прототип на Streamlit. Папка сохранена для справки и не изменяется.

## Запуск

Backend:

```powershell
cd backend
.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

Интерфейс открывается по адресу `http://localhost:5173`, документация API — `http://localhost:8000/docs`. Запросы с интерфейса на `/api` проксируются на backend.
