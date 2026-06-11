import { motion } from 'framer-motion'
import { Square, Volume2 } from 'lucide-react'
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis'

export default function TTSButton({ text }: { text: string }) {
  const { speak, stop, isSpeaking } = useSpeechSynthesis()

  if (isSpeaking) {
    return (
      <button
        onClick={stop}
        className="inline-flex items-center gap-2 rounded-xl border border-red-500 bg-red-100 px-4 py-2 font-semibold text-red-700 hover:bg-red-200"
      >
        <Square className="h-4 w-4 fill-current" />
        Stop
        <span className="flex items-end gap-0.5">
          {[0, 1, 2, 3].map((i) => (
            <motion.span
              key={i}
              className="w-1 rounded-full bg-red-500"
              animate={{ height: [4, 14, 4] }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                delay: i * 0.15,
                ease: 'easeInOut',
              }}
            />
          ))}
        </span>
      </button>
    )
  }

  return (
    <button
      onClick={() => speak(text)}
      className="inline-flex items-center gap-2 rounded-xl border border-emerald-500 bg-white px-4 py-2 font-semibold text-emerald-600 hover:bg-emerald-50"
    >
      <Volume2 className="h-5 w-5" />
      Listen
    </button>
  )
}
