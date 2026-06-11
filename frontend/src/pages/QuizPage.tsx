import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star } from 'lucide-react'
import client from '../api/client'
import PageWrapper from '../components/layout/PageWrapper'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import ProgressBar from '../components/ui/ProgressBar'
import ObjectiveQuiz from '../components/quiz/ObjectiveQuiz'
import TheoryQuiz from '../components/quiz/TheoryQuiz'
import OralQuiz from '../components/quiz/OralQuiz'
import type {
  AnsweredQuestion,
  AnswerResult,
  Lesson,
  Question,
  QuizCompleteResult,
} from '../types'

export default function QuizPage() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [current, setCurrent] = useState(0)
  const [xpEarned, setXpEarned] = useState(0)
  const [answered, setAnswered] = useState<AnsweredQuestion[]>([])
  const [error, setError] = useState('')
  const [pendingComplete, setPendingComplete] = useState<AnsweredQuestion[] | null>(null)
  const [finishing, setFinishing] = useState(false)
  const questionStart = useRef(Date.now())

  useEffect(() => {
    const load = async () => {
      try {
        const [lessonRes, startRes] = await Promise.all([
          client.get(`/lessons/${lessonId}`),
          client.post('/quiz/start', { lesson_id: Number(lessonId) }),
        ])
        setLesson(lessonRes.data)
        setSessionId(startRes.data.session_id)
        setQuestions(startRes.data.questions)
        questionStart.current = Date.now()
      } catch (err: any) {
        setError(err.response?.data?.error ?? 'Could not start the quiz.')
      }
    }
    load()
  }, [lessonId])

  const question = questions[current]

  const submitAnswer = async (answer: string): Promise<AnswerResult> => {
    const { data } = await client.post('/quiz/answer', {
      session_id: sessionId,
      question_id: question.id,
      answer,
      response_time_ms: Date.now() - questionStart.current,
    })
    setXpEarned((xp) => xp + (data.xp_earned ?? 0))
    return data
  }

  const skipQuestion = async () => {
    const label =
      question.type === 'oral' ? '(practiced in chat)' : '(skipped)'
    const { data } = await client.post('/quiz/answer', {
      session_id: sessionId,
      question_id: question.id,
      answer: label,
      skipped: true,
      response_time_ms: Date.now() - questionStart.current,
    })
    handleNext(label, data)
  }

  const finishQuiz = async (record: AnsweredQuestion[]) => {
    setFinishing(true)
    try {
      const { data } = await client.post<QuizCompleteResult>('/quiz/complete', {
        session_id: sessionId,
      })
      navigate(`/results/${sessionId}`, {
        state: {
          answered: record,
          complete: data,
          lessonTitle: lesson?.title,
          xpFromQuestions: record.reduce(
            (sum, a) => sum + (a.result.xp_earned ?? 0),
            0,
          ),
        },
      })
    } catch {
      setPendingComplete(record)
    } finally {
      setFinishing(false)
    }
  }

  const handleNext = (answer: string, result: AnswerResult) => {
    const record = [...answered, { question, userAnswer: answer, result }]
    setAnswered(record)

    if (current + 1 < questions.length) {
      setCurrent(current + 1)
      questionStart.current = Date.now()
    } else {
      finishQuiz(record)
    }
  }

  if (error) {
    return (
      <PageWrapper>
        <Card className="text-center">
          <p className="mb-4 font-semibold text-red-700">{error}</p>
          <button
            onClick={() => navigate('/lessons')}
            className="font-semibold text-emerald-600 hover:underline"
          >
            Back to lessons
          </button>
        </Card>
      </PageWrapper>
    )
  }

  if (pendingComplete) {
    return (
      <PageWrapper>
        <Card className="mx-auto max-w-md text-center">
          <p className="mb-4 font-semibold text-red-700">
            Could not save your quiz results. Check your connection and try
            again.
          </p>
          <Button loading={finishing} onClick={() => finishQuiz(pendingComplete)}>
            Retry
          </Button>
        </Card>
      </PageWrapper>
    )
  }

  if (!question) {
    return (
      <PageWrapper>
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between">
            <h1 className="text-lg font-bold text-gray-900">{lesson?.title}</h1>
            <span className="flex items-center gap-1 font-bold text-amber-600">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              +{xpEarned} XP
            </span>
          </div>
          <div className="mb-1 text-sm font-semibold text-gray-500">
            Question {current + 1} of {questions.length}
          </div>
          <ProgressBar value={((current + 1) / questions.length) * 100} />
        </div>

        <Card>
          <motion.div
            key={question.id}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
          >
            {question.type === 'objective' && (
              <ObjectiveQuiz
                question={question}
                onSubmit={submitAnswer}
                onNext={handleNext}
              />
            )}
            {question.type === 'theory' && (
              <TheoryQuiz
                question={question}
                onSubmit={submitAnswer}
                onNext={handleNext}
              />
            )}
            {question.type === 'oral' && (
              <OralQuiz
                question={question}
                onSubmit={submitAnswer}
                onNext={handleNext}
                onSkip={skipQuestion}
              />
            )}
          </motion.div>
        </Card>
      </div>
    </PageWrapper>
  )
}
