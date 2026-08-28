/**
 * Strip Markdown formatting down to text a screen-reader or the browser's
 * SpeechSynthesis API can narrate cleanly.
 *
 * The on-screen render always uses the full Markdown via `react-markdown`;
 * this utility is only for the TTS button (and any other narrator that
 * cannot interpret Markdown syntax).
 */
export function markdownToSpeakableText(md: string): string {
  if (!md) return ''
  return md
    // Heading markers at the start of a line
    .replace(/^#{1,6}\s+/gm, '')
    // Bold **text** → text
    .replace(/\*\*(.+?)\*\*/g, '$1')
    // Italic *text* or _text_ → text
    .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1$2')
    .replace(/(^|[^_])_([^_\n]+)_(?!_)/g, '$1$2')
    // Inline code `x` → x
    .replace(/`([^`]+)`/g, '$1')
    // Emoji tick / cross markers used in "Common Mistakes"
    .replace(/[❌✅]/g, '')
    // Bullet markers at the start of a line
    .replace(/^\s*[-*]\s+/gm, '')
    // Numbered list markers ("1. text" → "text")
    .replace(/^\s*\d+\.\s+/gm, '')
    // Blockquote markers
    .replace(/^\s*>\s+/gm, '')
    // The em-dash-space idiom used to separate example + note; keep as a pause
    .replace(/\s—\s/g, ', ')
    // Collapse two-or-more blank lines into a spoken pause
    .replace(/\n{2,}/g, '. ')
    // Any remaining single newline becomes a light pause
    .replace(/\n/g, ' ')
    // Squash any run of spaces
    .replace(/\s{2,}/g, ' ')
    .trim()
}

/** Prefer content_markdown when present, otherwise fall back to legacy content. */
export function lessonBodyForDisplay(lesson: {
  content_markdown?: string
  content: string
}): string {
  return lesson.content_markdown && lesson.content_markdown.trim().length > 0
    ? lesson.content_markdown
    : lesson.content
}
