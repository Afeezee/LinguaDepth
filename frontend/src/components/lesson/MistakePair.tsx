import type { ReactNode } from 'react'

/**
 * Renders one "❌ wrong → ✅ right — reason" bullet from a lesson's Common
 * Mistakes section as two side-by-side coloured chips followed by the
 * explanation, so learners can see the correction at a glance instead of
 * decoding an inline emoji sequence.
 *
 * Falls back gracefully to plain text when the bullet doesn't match the
 * template — the raw string is rendered as-is.
 */
export default function MistakePair({ children }: { children: ReactNode }) {
  const text = extractText(children)
  const parsed = parseMistake(text)

  if (!parsed) {
    return <li className="text-gray-700">{children}</li>
  }

  const { wrong, right, reason } = parsed

  return (
    <li className="my-2 list-none">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-stretch">
        <span className="inline-flex flex-1 items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 line-through decoration-red-400">
          <span aria-hidden className="mt-0.5 shrink-0">❌</span>
          <span className="min-w-0 break-words">{wrong}</span>
        </span>
        <span className="hidden self-center text-gray-400 sm:inline">→</span>
        <span className="inline-flex flex-1 items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800">
          <span aria-hidden className="mt-0.5 shrink-0">✅</span>
          <span className="min-w-0 break-words">{right}</span>
        </span>
      </div>
      {reason && (
        <p className="mt-1 text-xs italic text-gray-600">{reason}</p>
      )}
    </li>
  )
}

function extractText(node: ReactNode): string {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(extractText).join('')
  if (typeof node === 'object' && 'props' in (node as any)) {
    return extractText((node as any).props.children)
  }
  return ''
}

function parseMistake(text: string): { wrong: string; right: string; reason?: string } | null {
  // Expected shape: "❌ wrong → ✅ right — reason"
  const cleaned = text.replace(/\s+/g, ' ').trim()
  const match = cleaned.match(/^❌\s*(.+?)\s*→\s*✅\s*(.+?)(?:\s*—\s*(.+))?$/u)
  if (!match) return null
  const [, wrong, right, reason] = match
  return { wrong: wrong.trim(), right: right.trim(), reason: reason?.trim() }
}

/** Detect whether a bullet <li> is a mistake pair line, before rendering. */
export function isMistakeLine(text: string): boolean {
  return /^❌.*→.*✅/u.test(text.replace(/\s+/g, ' ').trim())
}
