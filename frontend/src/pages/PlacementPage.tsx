import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import ProgressBar from '../components/ui/ProgressBar'
import type { Question } from '../types'

export default function PlacementPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<{ question_id: number; answer: string }[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadProgress, setLoadProgress] = useState(12)
  const [loadError, setLoadError] = useState('')
  const { refreshUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    let active = true

    client
      .get('/lessons/placement')
      .then(({ data }) => {
        if (!active) return

        if (!Array.isArray(data) || data.length === 0) {
          setLoadError(
            'The placement quiz is not available right now. Please try again shortly.',
          )
          return
        }

        setLoadProgress(100)
        setQuestions(data)
      })
      .catch(() => {
        if (!active) return
        setLoadError('Could not load the placement quiz. Please try again.')
      })
      .finally(() => {
        if (!active) return
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!loading) return

    const timer = window.setInterval(() => {
      setLoadProgress((currentProgress) => {
        if (currentProgress >= 92) return currentProgress
        return Math.min(currentProgress + 8, 92)
      })
    }, 250)

    return () => window.clearInterval(timer)
  }, [loading])

  const question = questions[current]

  const handleSelect = (option: string) => {
    if (selected) return
    setSelected(option)
    const updated = [...answers, { question_id: question.id, answer: option }]
    setAnswers(updated)

    setTimeout(async () => {
      if (current + 1 < questions.length) {
        setCurrent(current + 1)
        setSelected(null)
      } else {
        setSubmitting(true)
        try {
          await client.post('/quiz/placement/submit', { answers: updated })
          await refreshUser()
        } finally {
          navigate('/dashboard')
        }
      }
    }, 400)
  }

  if (loadError) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <Card className="text-center">
          <p className="mb-4 text-red-700">{loadError}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </Card>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="w-full max-w-md text-center">
          <h2 className="mb-2 text-xl font-bold text-gray-900">Preparing your quiz</h2>
          <p className="mb-5 text-sm text-gray-500">
            We&apos;re loading your placement questions.
          </p>
          <ProgressBar value={loadProgress} className="mb-2" />
          <p className="text-sm font-semibold text-emerald-600">{loadProgress}%</p>
        </Card>
      </div>
    )
  }

  if (submitting) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        <p className="font-semibold text-gray-500">Finding your level...</p>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <Card className="text-center">
          <p className="mb-4 text-red-700">
            The placement quiz is unavailable because no questions were returned.
          </p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-2xl">
        <div className="mb-6 text-center">
          <h1 className="mb-2 text-2xl font-extrabold text-gray-900">
            Let's see where you are! 🌱
          </h1>
          <p className="text-gray-500">
            Answer these 10 questions — no pressure.
          </p>
        </div>

        <div className="mb-6">
          <div className="mb-2 flex justify-between text-sm font-semibold text-gray-500">
            <span>Question {current + 1} of {questions.length}</span>
          </div>
          <ProgressBar value={((current + 1) / questions.length) * 100} />
        </div>

        <Card>
          <motion.div
            key={question.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h2 className="mb-6 text-xl font-bold text-gray-900">
              {question.question_text}
            </h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {(question.options ?? []).map((option) => (
                <button
                  key={option}
                  onClick={() => handleSelect(option)}
                  disabled={!!selected}
                  className={`rounded-xl border-2 p-4 text-left font-semibold transition-colors ${
                    selected === option
                      ? 'border-emerald-500 bg-emerald-50'
                      : 'border-gray-200 bg-white hover:border-emerald-300 hover:bg-emerald-50'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        </Card>
      </div>
    </div>
  )
}
