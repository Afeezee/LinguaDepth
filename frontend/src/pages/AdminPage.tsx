import { useEffect, useState } from 'react'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import {
  Activity,
  BookOpen,
  Download,
  FileQuestion,
  Search,
  Shield,
  ShieldOff,
  Trash2,
  TrendingUp,
  Users,
} from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import PageWrapper from '../components/layout/PageWrapper'
import Badge from '../components/ui/Badge'
import Card from '../components/ui/Card'
import type { AdminAnalytics, AdminUser, Level } from '../types'

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
)

type Tab = 'overview' | 'users' | 'export'

const LEVEL_COLORS: Record<Level, 'green' | 'amber' | 'purple'> = {
  beginner: 'green',
  intermediate: 'amber',
  advanced: 'purple',
}

const EXPORT_DATASETS = [
  { key: 'users', label: 'Users', note: 'Accounts, levels, XP, streaks' },
  { key: 'sessions', label: 'Quiz Sessions', note: 'Scores, timings, completion' },
  { key: 'answers', label: 'Question Answers', note: 'Every answer with LLM feedback' },
  { key: 'questions', label: 'Question Bank', note: 'All generated questions' },
  { key: 'progress', label: 'Lesson Progress', note: 'Completion per user per lesson' },
]

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users
  label: string
  value: string | number
}) {
  return (
    <Card className="flex items-center gap-4 !p-5">
      <div className="rounded-2xl bg-emerald-50 p-3">
        <Icon className="h-6 w-6 text-emerald-600" />
      </div>
      <div>
        <p className="text-2xl font-extrabold text-gray-900">{value}</p>
        <p className="text-sm font-medium text-gray-500">{label}</p>
      </div>
    </Card>
  )
}

export default function AdminPage() {
  const { user: me } = useAuth()
  const [tab, setTab] = useState<Tab>('overview')
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [search, setSearch] = useState('')
  const [busyUserId, setBusyUserId] = useState<number | null>(null)
  const [exporting, setExporting] = useState<string | null>(null)
  const [error, setError] = useState('')

  const loadAnalytics = () =>
    client.get('/admin/analytics').then(({ data }) => setAnalytics(data))
  const loadUsers = (q = '') =>
    client
      .get('/admin/users', { params: q ? { search: q } : {} })
      .then(({ data }) => setUsers(data))

  useEffect(() => {
    Promise.all([loadAnalytics(), loadUsers()]).catch(() =>
      setError('Could not load admin data.'),
    )
  }, [])

  const updateUser = async (id: number, body: Record<string, unknown>) => {
    setBusyUserId(id)
    setError('')
    try {
      await client.patch(`/admin/users/${id}`, body)
      await loadUsers(search)
    } catch (err: any) {
      setError(err.response?.data?.error ?? 'Update failed.')
    } finally {
      setBusyUserId(null)
    }
  }

  const deleteUser = async (target: AdminUser) => {
    if (
      !window.confirm(
        `Delete ${target.name} (${target.email})? This removes all their sessions and progress permanently.`,
      )
    )
      return
    setBusyUserId(target.id)
    setError('')
    try {
      await client.delete(`/admin/users/${target.id}`)
      await Promise.all([loadUsers(search), loadAnalytics()])
    } catch (err: any) {
      setError(err.response?.data?.error ?? 'Delete failed.')
    } finally {
      setBusyUserId(null)
    }
  }

  const exportCsv = async (dataset: string) => {
    setExporting(dataset)
    setError('')
    try {
      const { data } = await client.get(`/admin/export/${dataset}`, {
        responseType: 'blob',
      })
      const url = URL.createObjectURL(data)
      const link = document.createElement('a')
      link.href = url
      link.download = `linguadepth_${dataset}_${new Date().toISOString().slice(0, 10)}.csv`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch {
      setError('Export failed.')
    } finally {
      setExporting(null)
    }
  }

  const dayLabel = (iso: string) =>
    new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })

  return (
    <PageWrapper>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-emerald-600" />
          <h1 className="text-3xl font-extrabold text-gray-900">Admin</h1>
        </div>
        <div className="flex rounded-xl bg-gray-100 p-1">
          {(['overview', 'users', 'export'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded-lg px-5 py-2 font-semibold capitalize transition-colors ${
                tab === t
                  ? 'bg-white text-emerald-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="mb-4 rounded-xl bg-red-100 p-3 font-medium text-red-700">
          {error}
        </p>
      )}

      {/* ---------- Overview ---------- */}
      {tab === 'overview' &&
        (analytics ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard icon={Users} label="Total users" value={analytics.totals.users} />
              <StatCard
                icon={Activity}
                label="Active this week"
                value={analytics.totals.active_week}
              />
              <StatCard
                icon={TrendingUp}
                label="Avg quiz score"
                value={`${Math.round(analytics.totals.avg_score * 100)}%`}
              />
              <StatCard
                icon={BookOpen}
                label="Quizzes completed"
                value={analytics.totals.sessions_completed}
              />
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <h2 className="mb-4 font-bold text-gray-900">Signups — last 14 days</h2>
                <div className="h-56">
                  <Line
                    data={{
                      labels: analytics.signups_daily.map((d) => dayLabel(d.date)),
                      datasets: [
                        {
                          data: analytics.signups_daily.map((d) => d.count),
                          borderColor: '#10b981',
                          backgroundColor: 'rgba(16,185,129,0.15)',
                          fill: true,
                          tension: 0.35,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                    }}
                  />
                </div>
              </Card>

              <Card>
                <h2 className="mb-4 font-bold text-gray-900">
                  Quizzes completed — last 14 days
                </h2>
                <div className="h-56">
                  <Bar
                    data={{
                      labels: analytics.sessions_daily.map((d) => dayLabel(d.date)),
                      datasets: [
                        {
                          data: analytics.sessions_daily.map((d) => d.count),
                          backgroundColor: '#10b981',
                          borderRadius: 6,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                    }}
                  />
                </div>
              </Card>

              <Card>
                <h2 className="mb-4 font-bold text-gray-900">Learners by level</h2>
                <div className="mx-auto h-56 max-w-xs">
                  <Doughnut
                    data={{
                      labels: analytics.level_distribution.map((l) => l.level),
                      datasets: [
                        {
                          data: analytics.level_distribution.map((l) => l.count),
                          backgroundColor: ['#10b981', '#f59e0b', '#a855f7'],
                          borderWidth: 0,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { position: 'bottom' } },
                    }}
                  />
                </div>
              </Card>

              <Card>
                <h2 className="mb-4 font-bold text-gray-900">
                  Hardest topics platform-wide
                </h2>
                {analytics.weak_topics.length === 0 ? (
                  <p className="text-gray-500">No wrong answers recorded yet.</p>
                ) : (
                  <div className="h-56">
                    <Bar
                      data={{
                        labels: analytics.weak_topics.map((t) =>
                          t.topic.replace(/_/g, ' '),
                        ),
                        datasets: [
                          {
                            data: analytics.weak_topics.map((t) => t.wrong),
                            backgroundColor: '#f59e0b',
                            borderRadius: 6,
                          },
                        ],
                      }}
                      options={{
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
                      }}
                    />
                  </div>
                )}
              </Card>
            </div>

            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard icon={BookOpen} label="Lessons" value={analytics.totals.lessons} />
              <StatCard
                icon={FileQuestion}
                label="Questions in bank"
                value={analytics.totals.questions}
              />
              <StatCard
                icon={Activity}
                label="Active today"
                value={analytics.totals.active_today}
              />
              <StatCard
                icon={Users}
                label="Admins"
                value={users.filter((u) => u.is_admin).length}
              />
            </div>
          </div>
        ) : (
          <div className="flex justify-center py-20">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
          </div>
        ))}

      {/* ---------- Users ---------- */}
      {tab === 'users' && (
        <Card className="!p-0">
          <div className="flex items-center gap-2 border-b border-gray-200 p-4">
            <Search className="h-5 w-5 text-gray-400" />
            <input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                loadUsers(e.target.value)
              }}
              placeholder="Search by name or email..."
              className="flex-1 bg-transparent font-medium focus:outline-none"
            />
            <span className="text-sm font-semibold text-gray-500">
              {users.length} user{users.length === 1 ? '' : 's'}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-xs font-bold uppercase tracking-wide text-gray-500">
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Level</th>
                  <th className="px-4 py-3">XP</th>
                  <th className="px-4 py-3">Quizzes</th>
                  <th className="px-4 py-3">Avg Score</th>
                  <th className="px-4 py-3">Last Active</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <p className="flex items-center gap-1.5 font-bold text-gray-900">
                        {u.name}
                        {u.is_admin && (
                          <Shield className="h-3.5 w-3.5 text-emerald-600" />
                        )}
                      </p>
                      <p className="text-gray-500">{u.email}</p>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={u.level}
                        disabled={busyUserId === u.id}
                        onChange={(e) => updateUser(u.id, { level: e.target.value })}
                        className="rounded-lg border border-gray-200 bg-white px-2 py-1 font-semibold focus:border-emerald-500 focus:outline-none"
                      >
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                      </select>
                    </td>
                    <td className="px-4 py-3 font-semibold">{u.xp}</td>
                    <td className="px-4 py-3">{u.sessions_completed}</td>
                    <td className="px-4 py-3">
                      {u.avg_score != null ? (
                        <Badge
                          color={
                            u.avg_score >= 0.7
                              ? 'green'
                              : u.avg_score >= 0.4
                                ? 'amber'
                                : 'red'
                          }
                        >
                          {Math.round(u.avg_score * 100)}%
                        </Badge>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {u.last_active ?? 'never'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => updateUser(u.id, { is_admin: !u.is_admin })}
                          disabled={busyUserId === u.id || u.id === me?.id}
                          className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-bold transition-colors disabled:opacity-40 ${
                            u.is_admin
                              ? 'border-gray-200 text-gray-600 hover:bg-gray-100'
                              : 'border-emerald-500 text-emerald-600 hover:bg-emerald-50'
                          }`}
                        >
                          {u.is_admin ? (
                            <>
                              <ShieldOff className="h-3.5 w-3.5" />
                              Remove admin
                            </>
                          ) : (
                            <>
                              <Shield className="h-3.5 w-3.5" />
                              Make admin
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => deleteUser(u)}
                          disabled={busyUserId === u.id || u.id === me?.id}
                          title="Delete user"
                          className="rounded-lg p-2 text-gray-500 hover:bg-red-50 hover:text-red-600 disabled:opacity-40"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-10 text-center text-gray-500">
                      No users match your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* ---------- Export ---------- */}
      {tab === 'export' && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {EXPORT_DATASETS.map((d) => (
            <Card key={d.key} className="flex items-center justify-between gap-4">
              <div>
                <p className="font-bold text-gray-900">{d.label}</p>
                <p className="text-sm text-gray-500">{d.note}</p>
              </div>
              <button
                onClick={() => exportCsv(d.key)}
                disabled={exporting !== null}
                className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-emerald-600 disabled:opacity-50"
              >
                {exporting === d.key ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Download className="h-4 w-4" />
                )}
                CSV
              </button>
            </Card>
          ))}
        </div>
      )}
    </PageWrapper>
  )
}
