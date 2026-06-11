import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import PlacementPage from './pages/PlacementPage'
import DashboardPage from './pages/DashboardPage'
import LessonPage from './pages/LessonPage'
import QuizPage from './pages/QuizPage'
import ResultsPage from './pages/ResultsPage'
import ReportPage from './pages/ReportPage'
import AdminPage from './pages/AdminPage'
import type { ReactNode } from 'react'

function Spinner() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
    </div>
  )
}

function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/auth" replace />
  return <>{children}</>
}

function AdminOnly({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/auth" replace />
  if (!user.is_admin) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth" element={<LoginPage />} />
      <Route
        path="/placement"
        element={
          <Protected>
            <PlacementPage />
          </Protected>
        }
      />
      <Route
        path="/dashboard"
        element={
          <Protected>
            <DashboardPage />
          </Protected>
        }
      />
      <Route
        path="/lessons"
        element={
          <Protected>
            <LessonPage />
          </Protected>
        }
      />
      <Route
        path="/quiz/:lessonId"
        element={
          <Protected>
            <QuizPage />
          </Protected>
        }
      />
      <Route
        path="/results/:sessionId"
        element={
          <Protected>
            <ResultsPage />
          </Protected>
        }
      />
      <Route
        path="/report"
        element={
          <Protected>
            <ReportPage />
          </Protected>
        }
      />
      <Route
        path="/admin"
        element={
          <AdminOnly>
            <AdminPage />
          </AdminOnly>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
