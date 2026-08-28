import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import MistakePair, { isMistakeLine } from './MistakePair'

/**
 * Renders a lesson's Markdown body with lesson-specific styling:
 *  - Tailwind `prose` typography for headings, paragraphs, and lists
 *  - "❌ wrong → ✅ right" bullets in Common Mistakes rendered as
 *    coloured side-by-side chips via `MistakePair`
 *  - Bold text kept prominent so key examples stand out
 */
export default function LessonMarkdown({ source }: { source: string }) {
  return (
    <div className="prose prose-emerald max-w-none prose-headings:font-extrabold prose-h2:mt-0 prose-h2:text-2xl prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-2 prose-h3:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-900 prose-li:my-1 prose-ul:my-3">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          li: ({ children, ...props }) => {
            const text = childrenToText(children)
            if (isMistakeLine(text)) {
              return <MistakePair>{children}</MistakePair>
            }
            return <li {...props}>{children}</li>
          },
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  )
}

function childrenToText(node: unknown): string {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(childrenToText).join('')
  if (typeof node === 'object' && 'props' in (node as any)) {
    return childrenToText((node as any).props?.children)
  }
  return ''
}
