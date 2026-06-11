import { motion } from 'framer-motion'

interface ProgressBarProps {
  value: number // 0–100
  color?: string
  className?: string
}

export default function ProgressBar({
  value,
  color = 'bg-emerald-500',
  className = '',
}: ProgressBarProps) {
  return (
    <div className={`h-3 w-full overflow-hidden rounded-full bg-gray-200 ${className}`}>
      <motion.div
        className={`h-full rounded-full ${color}`}
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />
    </div>
  )
}
