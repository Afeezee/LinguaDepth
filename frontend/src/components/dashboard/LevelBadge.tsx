import { Award } from 'lucide-react'
import type { Level } from '../../types'
import Badge from '../ui/Badge'

const levelColors: Record<Level, 'green' | 'amber' | 'purple'> = {
  beginner: 'green',
  intermediate: 'amber',
  advanced: 'purple',
}

export default function LevelBadge({ level }: { level: Level }) {
  return (
    <Badge color={levelColors[level]}>
      <Award className="h-4 w-4" />
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </Badge>
  )
}
