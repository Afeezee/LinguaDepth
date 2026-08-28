import { useNavigate } from 'react-router-dom'
import { Clock, Play } from 'lucide-react'
import type { Lesson } from '../../types'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card from '../ui/Card'
import TTSButton from './TTSButton'
import LessonMarkdown from './LessonMarkdown'
import { lessonBodyForDisplay, markdownToSpeakableText } from '../../utils/markdown'

export default function LessonCard({ lesson }: { lesson: Lesson }) {
  const navigate = useNavigate()
  const body = lessonBodyForDisplay(lesson)
  const speakable = markdownToSpeakableText(body)

  return (
    <Card className="flex h-full flex-col">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-2xl font-extrabold text-gray-900">{lesson.title}</h2>
        <div className="flex flex-wrap items-center gap-2">
          {lesson.estimated_minutes ? (
            <Badge color="gray">
              <Clock className="mr-1 inline h-3 w-3" />
              {lesson.estimated_minutes} min
            </Badge>
          ) : null}
          <Badge color="gray">{lesson.topic.replace(/_/g, ' ')}</Badge>
        </div>
      </div>

      <div className="mb-6 flex-1">
        <LessonMarkdown source={body} />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <TTSButton text={speakable} />
        <Button onClick={() => navigate(`/quiz/${lesson.id}`)}>
          <Play className="h-5 w-5" />
          Start Quiz
        </Button>
      </div>
    </Card>
  )
}
