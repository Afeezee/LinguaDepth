import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Globe2 } from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

type Tab = 'login' | 'register'

export default function LoginPage() {
  const [searchParams] = useSearchParams()
  const [tab, setTab] = useState<Tab>(
    searchParams.get('mode') === 'register' ? 'register' : 'login',
  )
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = tab === 'login' ? '/auth/login' : '/auth/register'
      const body =
        tab === 'login' ? { email, password } : { name, email, password }
      const { data } = await client.post(endpoint, body)
      login(data.user, data.token)
      navigate(data.user?.is_admin ? '/dashboard' : data.needs_placement ? '/placement' : '/dashboard')
    } catch (err: any) {
      setError(
        err.response?.data?.error ?? 'Something went wrong. Please try again.',
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
          <p className="text-gray-500">
            Fun, bite-sized English lessons that adapt to you. 🇳🇬
          </p>
        </div>

        <Card>
          <div className="mb-6 flex rounded-xl bg-gray-100 p-1">
            {(['login', 'register'] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTab(t)
                  setError('')
                }}
                className={`flex-1 rounded-lg py-2 font-semibold transition-colors ${
                  tab === t
                    ? 'bg-white text-emerald-600 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900'
                }`}
              >
                {t === 'login' ? 'Log In' : 'Create Account'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === 'register' && (
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className={inputClass}
              />
            )}
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className={inputClass}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className={inputClass}
            />

            {error && (
              <p className="rounded-xl bg-red-100 p-3 text-sm font-medium text-red-700">
                {error}
              </p>
            )}

            <Button type="submit" loading={loading} className="w-full">
              {tab === 'login' ? 'Log In' : 'Start Learning'}
            </Button>
          </form>
        </Card>

        <p className="mt-6 text-center text-sm text-gray-500">
          {tab === 'login'
            ? 'New here? Create an account and take a quick placement quiz!'
            : "We'll find your level with a friendly 10-question quiz."}
        </p>
      </div>
    </div>
  )
}
