import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Mic, Send } from 'lucide-react'
import type { AnswerResult, Question } from '../../types'
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition'
import Button from '../ui/Button'
import TTSButton from '../lesson/TTSButton'
import SpeechChatbox from '../chatbox/SpeechChatbox'

interface OralQuizProps {
  question: Question
  onSubmit: (answer: string) => Promise<AnswerResult>
  onNext: (answer: string, result: AnswerResult) => void
  onSkip: () => Promise<void>
}

function scoreColor(score: number) {
  if (score >= 70) return 'bg-green-100 text-green-700'
  if (score >= 40) return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-700'
}

export default function OralQuiz({
  question,
  onSubmit,
  onNext,
  onSkip,
}: OralQuizProps) {
  const { start, stop, transcript, isListening, isSupported } =
    useSpeechRecognition()
  const [typedAnswer, setTypedAnswer] = useState('')
  const [validating, setValidating] = useState(false)
  const [advancing, setAdvancing] = useState(false)
  const [chatEnded, setChatEnded] = useState(false)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [submittedText, setSubmittedText] = useState('')

  // After the practice chat is ended, the learner can move on without a
  // graded answer — recorded as practiced, no XP.
  const handleContinueAfterChat = async () => {
    if (advancing || validating || result) return
    stop()
    setAdvancing(true)
    try {
      await onSkip()
    } finally {
      setAdvancing(false)
    }
  }

  useEffect(() => {
    setTypedAnswer('')
    setValidating(false)
    setAdvancing(false)
    setChatEnded(false)
    setResult(null)
    setSubmittedText('')
  }, [question.id])

  const answerText = isSupported ? transcript : typedAnswer

  const handleSubmit = async () => {
    const text = answerText.trim()
    if (!text || validating) return
    setSubmittedText(text)
    setValidating(true)
    try {
      const res = await onSubmit(text)
      setResult(res)
    } finally {
      setValidating(false)
    }
  }

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <h2 className="text-2xl font-bold text-gray-900">
          {question.question_text}
        </h2>
        <TTSButton text={question.question_text} />
      </div>

      {isSupported ? (
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            {isListening && (
              <motion.span
                className="absolute inset-0 rounded-full border-4 border-red-400"
                animate={{ scale: [1, 1.4], opacity: [0.8, 0] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: 'easeOut' }}
              />
            )}
            <motion.button
              onClick={isListening ? stop : start}
              disabled={!!result}
              animate={isListening ? {} : { scale: [1, 1.06, 1] }}
              transition={{ duration: 1.6, repeat: Infinity }}
              className={`relative flex h-24 w-24 items-center justify-center rounded-full text-white shadow-md transition-colors disabled:opacity-50 ${
                isListening ? 'bg-red-500' : 'bg-emerald-500 hover:bg-emerald-600'
              }`}
            >
              <Mic className="h-10 w-10" />
            </motion.button>
          </div>
          <p className="font-semibold text-gray-500">
            {isListening ? 'Listening…' : 'Tap the mic and speak your answer'}
          </p>
        </div>
      ) : (
        <div>
          <p className="mb-3 rounded-xl bg-amber-100 p-3 text-sm text-amber-700">
            Speech features require Chrome or Edge. You can type your answer
            instead.
          </p>
          <textarea
            rows={2}
            value={typedAnswer}
            onChange={(e) => setTypedAnswer(e.target.value)}
            disabled={!!result}
            placeholder="Type your answer here..."
            className="w-full rounded-xl border border-gray-200 p-4 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          />
        </div>
      )}

      {answerText.trim() && !result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-5 rounded-2xl bg-gray-100 p-4"
        >
          <p className="text-sm text-gray-500">You said:</p>
          <p className="font-semibold text-gray-900">“{answerText.trim()}”</p>
        </motion.div>
      )}

      {!result && answerText.trim() && !isListening && (
        <Button onClick={handleSubmit} loading={validating} className="mt-4">
          <Send className="h-4 w-4" />
          {validating ? 'Checking your answer...' : 'Submit Answer'}
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
              {result.correct ? 'Great speaking!' : 'Keep practising!'}
            </span>
          </div>
          {result.feedback && <p className="text-sm">{result.feedback}</p>}
          <Button
            variant="secondary"
            className="mt-4 !py-2"
            onClick={() => onNext(submittedText, result)}
          >
            Continue
          </Button>
        </motion.div>
      )}

      <div className="mt-10 border-t border-gray-200 pt-6">
        <SpeechChatbox
          topic={question.question_text}
          defaultOpen={false}
          onOpenChange={(open) => setChatEnded(!open)}
        />

        {chatEnded && !result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <Button onClick={handleContinueAfterChat} loading={advancing}>
              Continue Quiz
              <ArrowRight className="h-5 w-5" />
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  )
}
