import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Clock,
} from 'lucide-react'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import client from '../api/client'
import PageWrapper from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import type { ReportData } from '../types'

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  BarElement,
  Tooltip,
)

export default function ReportPage() {
  const navigate = useNavigate()
  const [report, setReport] = useState<ReportData | null>(null)

  useEffect(() => {
    client.get('/dashboard/report').then(({ data }) => setReport(data))
  }, [])

  return (
    <PageWrapper>
      <button
        onClick={() => navigate('/dashboard')}
        className="mb-6 flex items-center gap-2 font-semibold text-gray-500 hover:text-gray-900"
      >
        <ArrowLeft className="h-5 w-5" />
        Back to Dashboard
      </button>

      <h1 className="mb-6 text-3xl font-extrabold text-gray-900">
        Your Learning Report
      </h1>

      {!report ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              Weekly Average Score
            </h2>
            <div className="h-64">
              <Line
                data={{
                  labels: report.weekly_scores.map((d) =>
                    new Date(d.date).toLocaleDateString('en-US', {
                      weekday: 'short',
                    }),
                  ),
                  datasets: [
                    {
                      data: report.weekly_scores.map((d) =>
                        Math.round(d.avg_score * 100),
                      ),
                      borderColor: '#10b981',
                      backgroundColor: 'rgba(16,185,129,0.15)',
                      fill: true,
                      tension: 0.35,
                      pointBackgroundColor: '#10b981',
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      ticks: { callback: (v) => `${v}%` },
                    },
                  },
                }}
              />
            </div>
          </Card>

          <Card>
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              Weakest Topics
            </h2>
            <div className="h-64">
              {report.wrong_by_topic.length === 0 ? (
                <p className="text-gray-500">
                  No wrong answers yet — keep it up! 🎉
                </p>
              ) : (
                <Bar
                  data={{
                    labels: report.wrong_by_topic.map((t) =>
                      t.topic.replace(/_/g, ' '),
                    ),
                    datasets: [
                      {
                        data: report.wrong_by_topic.map((t) => t.count),
                        backgroundColor: '#f59e0b',
                        borderRadius: 8,
                      },
                    ],
                  }}
                  options={{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
                  }}
                />
              )}
            </div>
          </Card>

          <Card className="lg:col-span-2">
            <div className="flex items-center gap-4">
              <div className="rounded-2xl bg-emerald-50 p-4">
                <Clock className="h-8 w-8 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-500">
                  Your average quiz time
                </p>
                <p className="text-2xl font-extrabold text-gray-900">
                  {report.avg_quiz_time} seconds per question
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </PageWrapper>
  )
}
