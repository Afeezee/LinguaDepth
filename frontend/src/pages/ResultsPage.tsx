import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle2, Home, Trophy, XCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import PageWrapper from '../components/layout/PageWrapper'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import type { AnsweredQuestion, Level, QuizCompleteResult } from '../types'

interface ResultsState {
  answered: AnsweredQuestion[]
  complete: QuizCompleteResult
  lessonTitle?: string
  xpFromQuestions: number
}

function ScoreCircle({ correct, total }: { correct: number; total: number }) {
  const pct = total ? correct / total : 0
  const radius = 56
  const circumference = 2 * Math.PI * radius

  return (
    <div className="relative h-36 w-36">
      <svg className="h-36 w-36 -rotate-90" viewBox="0 0 128 128">
        <circle
          cx="64" cy="64" r={radius}
          fill="none" stroke="#e5e7eb" strokeWidth="10"
        />
        <motion.circle
          cx="64" cy="64" r={radius}
          fill="none"
          stroke={pct >= 0.7 ? '#10b981' : pct >= 0.4 ? '#f59e0b' : '#ef4444'}
          strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - pct) }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-extrabold text-gray-900">
          {correct}/{total}
        </span>
        <span className="text-xs font-semibold text-gray-500">correct</span>
      </div>
    </div>
  )
}

function XPCountUp({ target }: { target: number }) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target <= 0) return
    const duration = 1000
    const start = performance.now()
    let frame: number
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration)
      setValue(Math.round(progress * target))
      if (progress < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target])
  return <span>+{value} XP</span>
}

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const state = location.state as ResultsState | null

  useEffect(() => {
    refreshUser().catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (!state) {
    return (
      <PageWrapper>
        <Card className="text-center">
          <p className="mb-4 text-gray-500">No quiz results to show.</p>
          <Button onClick={() => navigate('/lessons')}>Go to Lessons</Button>
        </Card>
      </PageWrapper>
    )
  }

  const { answered, complete, lessonTitle, xpFromQuestions } = state
  const correctCount = answered.filter((a) => a.result.correct).length
  const totalXp = xpFromQuestions + complete.xp_earned

  return (
    <PageWrapper>
      <div className="mx-auto max-w-2xl">
        {complete.level_changed && (
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 flex items-center gap-3 rounded-2xl bg-purple-100 p-4 text-purple-700"
          >
            <Trophy className="h-6 w-6" />
            <p className="font-bold">
              Level up! You're now {complete.new_level}. 🎉
            </p>
          </motion.div>
        )}

        <Card className="mb-6 flex flex-col items-center text-center">
          <h1 className="mb-1 text-2xl font-extrabold text-gray-900">
            Quiz Complete!
          </h1>
          {lessonTitle && <p className="mb-5 text-gray-500">{lessonTitle}</p>}
          <ScoreCircle correct={correctCount} total={answered.length} />
          <p className="mt-4 text-xl font-extrabold text-amber-600">
            <XPCountUp target={totalXp} />
          </p>
        </Card>

        <Card className="mb-6">
          <h2 className="mb-4 text-lg font-bold text-gray-900">Breakdown</h2>
          <div className="space-y-4">
            {answered.map(({ question, userAnswer, result }, i) => (
              <div
                key={question.id}
                className="rounded-xl border border-gray-200 p-4"
              >
                <div className="mb-2 flex items-start gap-2">
                  {result.correct ? (
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-700" />
                  ) : (
                    <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-700" />
                  )}
                  <p className="font-semibold text-gray-900">
                    {i + 1}. {question.question_text}
                  </p>
                </div>
                <div className="ml-7 space-y-1 text-sm">
                  <p className="text-gray-500">
                    Your answer:{' '}
                    <span className="font-medium text-gray-900">{userAnswer}</span>
                  </p>
                  {result.correct_answer && !result.correct && (
                    <p className="text-gray-500">
                      Correct answer:{' '}
                      <span className="font-medium text-green-700">
                        {result.correct_answer}
                      </span>
                    </p>
                  )}
                  {(result.feedback ?? result.explanation) && (
                    <p className="rounded-lg bg-gray-50 p-2 text-gray-700">
                      {result.feedback ?? result.explanation}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="flex flex-wrap gap-4">
          <Button onClick={() => navigate('/lessons')} className="flex-1">
            Next Lesson
            <ArrowRight className="h-5 w-5" />
          </Button>
          <Button
            variant="secondary"
            onClick={() =>
              navigate('/dashboard', {
                state: complete.level_changed
                  ? { newLevel: complete.new_level as Level }
                  : undefined,
              })
            }
            className="flex-1"
          >
            <Home className="h-5 w-5" />
            Go to Dashboard
          </Button>
        </div>
      </div>
    </PageWrapper>
  )
}
