import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { getToken, removeToken } from './api/client'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Deals from './pages/Deals'
import DealDetail from './pages/DealDetail'

// Верхняя панель с навигацией и выходом из аккаунта.
function Navigation() {
  const navigate = useNavigate()
  const authenticated = Boolean(getToken())

  function handleLogout(): void {
    removeToken()
    navigate('/login')
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <nav className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
        <Link to="/deals" className="font-semibold text-slate-900">
          Logist Docs Agent
        </Link>
        {authenticated ? (
          <button
            type="button"
            onClick={handleLogout}
            className="ml-auto text-sm text-slate-600 hover:text-slate-900"
          >
            Выйти
          </button>
        ) : (
          <>
            <Link
              to="/login"
              className="ml-auto text-sm text-slate-600 hover:text-slate-900"
            >
              Вход
            </Link>
            <Link to="/register" className="text-sm text-slate-600 hover:text-slate-900">
              Регистрация
            </Link>
          </>
        )}
      </nav>
    </header>
  )
}

// Корневой компонент с маршрутами приложения.
function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navigation />
        <main className="mx-auto max-w-5xl px-4 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/deals" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/deals" element={<Deals />} />
              <Route path="/deals/:dealId" element={<DealDetail />} />
            </Route>
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
