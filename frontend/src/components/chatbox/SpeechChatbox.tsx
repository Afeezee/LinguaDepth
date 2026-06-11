import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Mic, MessageCircle, Send, X } from 'lucide-react'
import client from '../../api/client'
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition'
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis'
import type { ChatMessage } from '../../types'

const OPENER = "Hi! Let's practice talking. Tell me about yourself."
const MAX_TURNS = 10
const WRAP_UP_AFTER_TURNS = 5

interface SpeechChatboxProps {
  topic: string
  defaultOpen?: boolean
  /** Fired when the user opens or ends the chat (not on mount). */
  onOpenChange?: (open: boolean) => void
}

export default function SpeechChatbox({
  topic,
  defaultOpen = true,
  onOpenChange,
}: SpeechChatboxProps) {
  const [open, setOpen] = useState(defaultOpen)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: OPENER },
  ])
  const [sending, setSending] = useState(false)
  const [typedInput, setTypedInput] = useState('')
  const recognition = useSpeechRecognition()
  const { start, stop, transcript, isListening, isSupported } = recognition
  const { speak, stop: stopSpeaking } = useSpeechSynthesis()
  const scrollRef = useRef<HTMLDivElement>(null)
  const lastSent = useRef('')

  const userTurns = messages.filter((m) => m.role === 'user').length

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [messages])

  const endChat = () => {
    stop()
    stopSpeaking()
    setOpen(false)
    onOpenChange?.(false)
  }

  const openChat = () => {
    setOpen(true)
    onOpenChange?.(true)
  }

  const send = async (text: string) => {
    const content = text.trim()
    if (!content || sending) return
    setSending(true)
    const history = messages.slice(-MAX_TURNS)
    setMessages((prev) => [...prev, { role: 'user', content }])
    try {
      const { data } = await client.post('/llm/chat', {
        message: content,
        history,
        topic,
      })
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }])
      speak(data.reply)
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: "Sorry, I couldn't hear you. Try again!" },
      ])
    } finally {
      setSending(false)
    }
  }

  // When the mic stops with a final transcript, send it once
  useEffect(() => {
    if (!isListening && transcript.trim() && transcript !== lastSent.current) {
      lastSent.current = transcript
      send(transcript)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isListening])

  if (!open) {
    return (
      <button
        onClick={openChat}
        className="inline-flex items-center gap-2 rounded-xl border border-emerald-500 bg-white px-4 py-2 text-sm font-semibold text-emerald-600 hover:bg-emerald-50"
      >
        <MessageCircle className="h-4 w-4" />
        {userTurns > 0
          ? 'Resume practice chat'
          : 'Want extra practice? Chat with your AI tutor'}
      </button>
    )
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5 text-emerald-500" />
          <h3 className="font-bold text-gray-900">Practice Chat</h3>
          <span className="text-xs font-medium text-gray-500">(optional)</span>
        </div>
        <button
          onClick={endChat}
          className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-sm font-semibold text-gray-500 hover:bg-gray-100 hover:text-gray-900"
          title="End practice chat"
        >
          <X className="h-4 w-4" />
          End chat
        </button>
      </div>

      <div
        ref={scrollRef}
        className="mb-4 max-h-72 space-y-3 overflow-y-auto rounded-2xl border border-gray-200 bg-gray-50 p-4"
      >
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm font-medium shadow-sm ${
                msg.role === 'assistant'
                  ? 'bg-emerald-500 text-white'
                  : 'border border-gray-200 bg-white text-gray-900'
              }`}
            >
              {msg.content}
            </div>
          </motion.div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-emerald-500 px-4 py-2 text-sm text-white">
              <span className="inline-flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="h-1.5 w-1.5 rounded-full bg-white"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </span>
            </div>
          </div>
        )}
      </div>

      {userTurns >= WRAP_UP_AFTER_TURNS && (
        <p className="mb-3 rounded-xl bg-emerald-50 p-3 text-center text-sm font-medium text-emerald-700">
          Great practice! 🎉 Keep chatting, or end the chat when you're ready
          to continue your quiz.
        </p>
      )}

      {isSupported ? (
        <div className="flex items-center justify-center gap-3">
          <div className="relative">
            {isListening && (
              <motion.span
                className="absolute inset-0 rounded-full border-2 border-red-400"
                animate={{ scale: [1, 1.5], opacity: [0.8, 0] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: 'easeOut' }}
              />
            )}
            <button
              onClick={isListening ? stop : start}
              disabled={sending}
              className={`relative flex h-14 w-14 items-center justify-center rounded-full text-white shadow-md transition-colors disabled:opacity-50 ${
                isListening ? 'bg-red-500' : 'bg-emerald-500 hover:bg-emerald-600'
              }`}
            >
              <Mic className="h-6 w-6" />
            </button>
          </div>
          <p className="text-sm font-semibold text-gray-500">
            {isListening ? 'Listening…' : 'Tap to talk'}
          </p>
        </div>
      ) : (
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            send(typedInput)
            setTypedInput('')
          }}
        >
          <input
            value={typedInput}
            onChange={(e) => setTypedInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-xl border border-gray-200 px-4 py-2 focus:border-emerald-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={sending || !typedInput.trim()}
            className="rounded-xl bg-emerald-500 p-2.5 text-white hover:bg-emerald-600 disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      )}
    </div>
  )
}
