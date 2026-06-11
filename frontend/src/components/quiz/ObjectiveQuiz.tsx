import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import type { AnswerResult, Question } from '../../types'

interface ObjectiveQuizProps {
  question: Question
  onSubmit: (answer: string) => Promise<AnswerResult>
  onNext: (answer: string, result: AnswerResult) => void
}

export default function ObjectiveQuiz({
  question,
  onSubmit,
  onNext,
}: ObjectiveQuizProps) {
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const timers = useRef<number[]>([])

  useEffect(() => {
    setSelected(null)
    setResult(null)
    return () => timers.current.forEach(clearTimeout)
  }, [question.id])

  const handleSelect = (option: string) => {
    if (selected) return
    setSelected(option)
    timers.current.push(
      window.setTimeout(async () => {
        const res = await onSubmit(option)
        setResult(res)
        timers.current.push(
          window.setTimeout(() => onNext(option, res), 1500),
        )
      }, 300),
    )
  }

  const optionStyle = (option: string) => {
    if (!result || option !== selected) {
      return option === selected
        ? 'border-emerald-500 bg-emerald-50'
        : 'border-gray-200 bg-white hover:border-emerald-300 hover:bg-emerald-50'
    }
    return result.correct
      ? 'border-green-500 bg-green-100 text-green-700'
      : 'border-red-500 bg-red-100 text-red-700'
  }

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-gray-900">
        {question.question_text}
      </h2>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {(question.options ?? []).map((option) => (
          <motion.button
            key={option}
            onClick={() => handleSelect(option)}
            disabled={!!selected}
            className={`rounded-xl border-2 p-4 text-left font-semibold transition-colors disabled:cursor-default ${optionStyle(option)}`}
            animate={
              result && option === selected
                ? result.correct
                  ? { scale: [1, 1.05, 1] }
                  : { x: [0, -5, 5, -5, 5, -5, 0] }
                : {}
            }
            transition={{ duration: result?.correct ? 0.3 : 0.4 }}
          >
            {option}
          </motion.button>
        ))}
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-5 rounded-xl p-4 ${
            result.correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}
        >
          <p className="font-bold">
            {result.correct ? 'Correct! 🎉' : `Not quite — the answer is "${result.correct_answer}"`}
          </p>
          {result.explanation && <p className="mt-1 text-sm">{result.explanation}</p>}
        </motion.div>
      )}
    </div>
  )
}
