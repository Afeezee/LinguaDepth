import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Globe2 } from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) setError('This reset link is missing its token.')
  }, [token])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      const { data } = await client.post('/auth/reset-password', {
        token,
        password,
      })
      login(data.user, data.token)
      navigate(data.user?.is_admin ? '/dashboard' : '/dashboard')
    } catch (err: any) {
      setError(
        err.response?.data?.error ??
          'Could not reset your password. The link may have expired.',
      )
    } finally {
      setLoading(false)
    }
  }

  const inputClass =
    'w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200'

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link to="/" className="mb-3 inline-flex items-center justify-center gap-2">
            <Globe2 className="h-10 w-10 text-emerald-500" />
            <h1 className="text-3xl font-extrabold text-gray-900">
              Lingua<span className="text-emerald-600">Depth</span>
            </h1>
          </Link>
          <p className="text-gray-500">Choose a new password</p>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="password"
              placeholder="New password (min 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className={inputClass}
              autoFocus
              disabled={!token}
            />
            <input
              type="password"
              placeholder="Confirm new password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={6}
              className={inputClass}
              disabled={!token}
            />

            {error && (
              <p className="rounded-xl bg-red-100 p-3 text-sm font-medium text-red-700">
                {error}
              </p>
            )}

            <Button
              type="submit"
              loading={loading}
              disabled={!token}
              className="w-full"
            >
              Set new password
            </Button>
          </form>
        </Card>

        <p className="mt-6 text-center text-sm text-gray-500">
          <Link to="/auth" className="font-semibold text-emerald-600 hover:underline">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
