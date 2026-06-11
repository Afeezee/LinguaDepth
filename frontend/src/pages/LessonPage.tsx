import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, Circle, Lock } from 'lucide-react'
import client from '../api/client'
import PageWrapper from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import LessonCard from '../components/lesson/LessonCard'
import type { Lesson } from '../types'

export default function LessonPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get('/lessons/')
      .then(({ data }) => {
        setLessons(data)
        const firstIncomplete = data.find((l: Lesson) => !l.completed)
        setSelectedId(firstIncomplete?.id ?? data[0]?.id ?? null)
      })
      .finally(() => setLoading(false))
  }, [])

  const core = lessons.filter((l) => l.path_type === 'core')
  const path = lessons.filter((l) => l.path_type === 'level_path')
  const allCoreDone = core.every((l) => l.completed)

  // A core lesson unlocks when all previous core lessons are complete;
  // the level path unlocks once all core lessons are done.
  const isLocked = useMemo(() => {
    return (lesson: Lesson) => {
      if (lesson.path_type === 'core') {
        const index = core.findIndex((l) => l.id === lesson.id)
        return core.slice(0, index).some((l) => !l.completed)
      }
      return !allCoreDone
    }
  }, [core, allCoreDone])

  const selected = lessons.find((l) => l.id === selectedId)

  const renderItem = (lesson: Lesson) => {
    const locked = isLocked(lesson)
    return (
      <button
        key={lesson.id}
        onClick={() => !locked && setSelectedId(lesson.id)}
        disabled={locked}
        className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors ${
          selectedId === lesson.id
            ? 'bg-emerald-50 text-emerald-600'
            : locked
              ? 'cursor-not-allowed text-gray-400'
              : 'text-gray-900 hover:bg-gray-50'
        }`}
      >
        {locked ? (
          <Lock className="h-5 w-5 shrink-0" />
        ) : lesson.completed ? (
          <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-500" />
        ) : (
          <Circle className="h-5 w-5 shrink-0 text-gray-300" />
        )}
        <span className="truncate text-sm font-semibold">{lesson.title}</span>
      </button>
    )
  }

  return (
    <PageWrapper>
      <h1 className="mb-6 text-3xl font-extrabold text-gray-900">Lessons</h1>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="h-fit lg:sticky lg:top-20">
            <h2 className="mb-2 px-3 text-xs font-bold uppercase tracking-wide text-gray-500">
              Core Lessons
            </h2>
            <div className="mb-4 space-y-1">{core.map(renderItem)}</div>

            <h2 className="mb-2 px-3 text-xs font-bold uppercase tracking-wide text-gray-500">
              Your Level Path
            </h2>
            <div className="space-y-1">{path.map(renderItem)}</div>
          </Card>

          <div className="lg:col-span-2">
            {selected ? (
              <LessonCard lesson={selected} />
            ) : (
              <Card>
                <p className="text-gray-500">Select a lesson to begin.</p>
              </Card>
            )}
          </div>
        </div>
      )}
    </PageWrapper>
  )
}
