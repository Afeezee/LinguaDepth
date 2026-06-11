import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Send } from 'lucide-react'
import type { AnswerResult, Question } from '../../types'
import Button from '../ui/Button'

interface TheoryQuizProps {
  question: Question
  onSubmit: (answer: string) => Promise<AnswerResult>
  onNext: (answer: string, result: AnswerResult) => void
}

function scoreColor(score: number) {
  if (score >= 70) return 'bg-green-100 text-green-700'
  if (score >= 40) return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-700'
}

export default function TheoryQuiz({ question, onSubmit, onNext }: TheoryQuizProps) {
  const [answer, setAnswer] = useState('')
  const [grading, setGrading] = useState(false)
  const [result, setResult] = useState<AnswerResult | null>(null)

  useEffect(() => {
    setAnswer('')
    setGrading(false)
    setResult(null)
  }, [question.id])

  const handleSubmit = async () => {
    if (!answer.trim() || grading) return
    setGrading(true)
    try {
      const res = await onSubmit(answer.trim())
      setResult(res)
    } finally {
      setGrading(false)
    }
  }

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-gray-900">
        {question.question_text}
      </h2>

      <textarea
        rows={3}
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        disabled={!!result || grading}
        placeholder="Write your answer here..."
        className="w-full rounded-xl border border-gray-200 p-4 text-gray-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200 disabled:bg-gray-50"
      />

      {!result && (
        <Button
          onClick={handleSubmit}
          loading={grading}
          disabled={!answer.trim()}
          className="mt-4"
        >
          <Send className="h-4 w-4" />
          {grading ? 'Grading your answer...' : 'Submit Answer'}
        </Button>
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-5 rounded-xl p-4 ${scoreColor(result.score ?? 0)}`}
        >
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-full bg-white/60 px-3 py-0.5 text-sm font-extrabold">
              {result.score}%
            </span>
            <span className="font-bold">
              {result.correct ? 'Well done!' : 'Keep practising!'}
            </span>
          </div>
          {result.feedback && <p className="text-sm">{result.feedback}</p>}
          <Button
            variant="secondary"
            className="mt-4 !py-2"
            onClick={() => onNext(answer.trim(), result)}
          >
            Continue
          </Button>
        </motion.div>
      )}
    </div>
  )
}
