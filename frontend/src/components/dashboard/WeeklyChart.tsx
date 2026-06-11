import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

interface WeeklyChartProps {
  data: { date: string; score: number }[]
}

export default function WeeklyChart({ data }: WeeklyChartProps) {
  const labels = data.map((d) =>
    new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' }),
  )
  return (
    <Bar
      data={{
        labels,
        datasets: [
          {
            data: data.map((d) => Math.round(d.score * 100)),
            backgroundColor: '#10b981',
            borderRadius: 8,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { callback: (v) => `${v}%` } },
        },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => `Score: ${ctx.parsed.y}%` } },
        },
      }}
    />
  )
}
