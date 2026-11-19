import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Deals from './pages/Deals'
import DealDetail from './pages/DealDetail'

// Корневой компонент с навигацией и объявлением маршрутов.
function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <header className="border-b border-slate-200 bg-white">
          <nav className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
            <Link to="/deals" className="font-semibold text-slate-900">
              Logist Docs Agent
            </Link>
            <Link
              to="/login"
              className="ml-auto text-sm text-slate-600 hover:text-slate-900"
            >
              Вход
            </Link>
            <Link to="/register" className="text-sm text-slate-600 hover:text-slate-900">
              Регистрация
            </Link>
          </nav>
        </header>

        <main className="mx-auto max-w-5xl px-4 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/deals" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/deals" element={<Deals />} />
            <Route path="/deals/:dealId" element={<DealDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
