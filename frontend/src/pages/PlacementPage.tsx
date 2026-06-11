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
  const [loadError, setLoadError] = useState('')
  const { refreshUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    client
      .get('/lessons/placement')
      .then(({ data }) => setQuestions(data))
      .catch(() => setLoadError('Could not load the placement quiz. Please try again.'))
  }, [])

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

  if (!question || submitting) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        <p className="font-semibold text-gray-500">
          {submitting ? 'Finding your level...' : 'Loading your quiz...'}
        </p>
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
