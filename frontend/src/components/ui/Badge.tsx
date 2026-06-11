import type { ReactNode } from 'react'

interface BadgeProps {
  color?: 'green' | 'amber' | 'purple' | 'red' | 'gray'
  children: ReactNode
  className?: string
}

const colors = {
  green: 'bg-green-100 text-green-700',
  amber: 'bg-amber-100 text-amber-700',
  purple: 'bg-purple-100 text-purple-700',
  red: 'bg-red-100 text-red-700',
  gray: 'bg-gray-100 text-gray-600',
}

export default function Badge({ color = 'gray', children, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-semibold ${colors[color]} ${className}`}
    >
      {children}
    </span>
  )
}
