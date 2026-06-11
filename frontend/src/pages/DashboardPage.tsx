import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BarChart3, BookOpen, CheckCircle2, PartyPopper, Star } from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import PageWrapper from '../components/layout/PageWrapper'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Modal from '../components/ui/Modal'
import ProgressBar from '../components/ui/ProgressBar'
import LevelBadge from '../components/dashboard/LevelBadge'
import StreakCounter from '../components/dashboard/StreakCounter'
import WeeklyChart from '../components/dashboard/WeeklyChart'
import type { DashboardStats, Level } from '../types'

function Confetti() {
  const pieces = Array.from({ length: 40 })
  const colors = ['#10b981', '#f59e0b', '#a855f7', '#ef4444', '#3b82f6']
  return (
    <div className="pointer-events-none fixed inset-0 z-[60] overflow-hidden">
      {pieces.map((_, i) => (
        <motion.span
          key={i}
          className="absolute h-2.5 w-2.5 rounded-sm"
          style={{
            left: `${(i * 97) % 100}%`,
            backgroundColor: colors[i % colors.length],
          }}
          initial={{ y: -20, rotate: 0, opacity: 1 }}
          animate={{ y: '105vh', rotate: 720, opacity: [1, 1, 0.6] }}
          transition={{
            duration: 2.5 + (i % 5) * 0.4,
            delay: (i % 8) * 0.1,
            ease: 'easeIn',
          }}
        />
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const { user, refreshUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [levelUp, setLevelUp] = useState<Level | null>(
    (location.state as { newLevel?: Level } | null)?.newLevel ?? null,
  )

  useEffect(() => {
    client.get('/dashboard/stats').then(({ data }) => setStats(data))
    refreshUser().catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const xpToNext = 500
  const xpProgress = stats ? ((stats.xp % xpToNext) / xpToNext) * 100 : 0

  return (
    <PageWrapper>
      {levelUp && <Confetti />}
      <Modal open={!!levelUp} onClose={() => setLevelUp(null)}>
        <div className="text-center">
          <PartyPopper className="mx-auto mb-4 h-14 w-14 text-amber-500" />
          <h2 className="mb-2 text-2xl font-extrabold text-gray-900">
            Level Up! 🎉
          </h2>
          <p className="mb-4 text-gray-500">
            Your hard work paid off — you've been promoted to
          </p>
          <div className="mb-6 flex justify-center">
            {levelUp && <LevelBadge level={levelUp} />}
          </div>
          <Button onClick={() => setLevelUp(null)} className="w-full">
            Keep Going!
          </Button>
        </div>
      </Modal>

      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900">
            Welcome back, {user?.name?.split(' ')[0]}! 👋
          </h1>
          <p className="text-gray-500">Ready for today's lesson?</p>
        </div>
        {user && <LevelBadge level={user.level} />}
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <div className="mb-2 flex items-center gap-2 text-gray-500">
            <Star className="h-5 w-5 fill-amber-400 text-amber-400" />
            <span className="text-sm font-semibold">XP Points</span>
          </div>
          <p className="mb-2 text-2xl font-extrabold text-gray-900">
            {stats?.xp ?? user?.xp ?? 0}
          </p>
          <ProgressBar value={xpProgress} color="bg-amber-400" />
        </Card>

        <Card>
          <div className="mb-2 flex items-center gap-2 text-gray-500">
            <CheckCircle2 className="h-5 w-5 text-emerald-500" />
            <span className="text-sm font-semibold">Lessons Completed</span>
          </div>
          <p className="mb-2 text-2xl font-extrabold text-gray-900">
            {stats ? `${stats.lessons_completed} / ${stats.total_lessons}` : '—'}
          </p>
          <ProgressBar value={stats?.completion_percent ?? 0} />
        </Card>

        <Card>
          <StreakCounter days={stats?.streak_days ?? user?.streak_days ?? 0} />
        </Card>
      </div>

      <Card className="mb-8">
        <h2 className="mb-4 text-lg font-bold text-gray-900">
          This Week's Performance
        </h2>
        <div className="h-56">
          {stats && <WeeklyChart data={stats.weekly_scores} />}
        </div>
      </Card>

      <div className="flex flex-wrap gap-4">
        <Button onClick={() => navigate('/lessons')} className="flex-1 sm:flex-none">
          <BookOpen className="h-5 w-5" />
          Continue Learning
        </Button>
        <Button
          variant="secondary"
          onClick={() => navigate('/report')}
          className="flex-1 sm:flex-none"
        >
          <BarChart3 className="h-5 w-5" />
          View Report
        </Button>
      </div>
    </PageWrapper>
  )
}
