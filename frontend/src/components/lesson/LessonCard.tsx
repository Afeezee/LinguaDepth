import { useNavigate } from 'react-router-dom'
import { Play } from 'lucide-react'
import type { Lesson } from '../../types'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card from '../ui/Card'
import TTSButton from './TTSButton'

export default function LessonCard({ lesson }: { lesson: Lesson }) {
  const navigate = useNavigate()

  return (
    <Card className="flex h-full flex-col">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-2xl font-extrabold text-gray-900">{lesson.title}</h2>
        <Badge color="gray">{lesson.topic.replace(/_/g, ' ')}</Badge>
      </div>

      <p className="mb-6 flex-1 text-lg leading-relaxed text-gray-700">
        {lesson.content}
      </p>

      <div className="flex flex-wrap items-center gap-3">
        <TTSButton text={lesson.content} />
        <Button onClick={() => navigate(`/quiz/${lesson.id}`)}>
          <Play className="h-5 w-5" />
          Start Quiz
        </Button>
      </div>
    </Card>
  )
}
