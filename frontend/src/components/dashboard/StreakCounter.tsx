import { motion } from 'framer-motion'
import { Flame } from 'lucide-react'

export default function StreakCounter({ days }: { days: number }) {
  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={{ scale: [1, 1.15, 1] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <Flame className="h-8 w-8 fill-orange-400 text-orange-500" />
      </motion.div>
      <div>
        <p className="text-2xl font-extrabold text-gray-900">{days}</p>
        <p className="text-sm text-gray-500">day streak</p>
      </div>
    </div>
  )
}
