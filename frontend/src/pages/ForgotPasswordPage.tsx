import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Globe2 } from 'lucide-react'
import client from '../api/client'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [devLink, setDevLink] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setDevLink(null)
    setLoading(true)
    try {
      const { data } = await client.post('/auth/forgot-password', { email })
      setMessage(data.message)
      // Backend returns debug_reset_link only when the server runs in
      // DEBUG mode — a dev-mode convenience so single-machine setups
      // don't need SMTP wired up before this flow can be tested.
      if (data.debug_reset_link) setDevLink(data.debug_reset_link)
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
          <p className="text-gray-500">Reset your password</p>
        </div>

        <Card>
          <h2 className="mb-2 text-xl font-bold text-gray-900">
            Forgot your password?
          </h2>
          <p className="mb-6 text-sm text-gray-500">
            Enter the email you signed up with and we'll send you a link to
            set a new password.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className={inputClass}
            />

            {error && (
              <p className="rounded-xl bg-red-100 p-3 text-sm font-medium text-red-700">
                {error}
              </p>
            )}

            {message && (
              <div className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">
                {message}
                {devLink && (
                  <div className="mt-2 rounded-lg bg-white p-2 text-xs text-gray-700">
                    <span className="font-semibold text-gray-500">
                      Dev-mode link:{' '}
                    </span>
                    <a
                      href={devLink}
                      className="break-all text-emerald-600 underline"
                    >
                      {devLink}
                    </a>
                  </div>
                )}
              </div>
            )}

            <Button type="submit" loading={loading} className="w-full">
              Send reset link
            </Button>
          </form>
        </Card>

        <p className="mt-6 text-center text-sm text-gray-500">
          Remembered it?{' '}
          <Link to="/auth" className="font-semibold text-emerald-600 hover:underline">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
