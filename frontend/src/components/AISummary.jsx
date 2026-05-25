import ReactMarkdown from 'react-markdown'
import { Sparkles } from 'lucide-react'

export default function AISummary({ text, title = 'AI Analysis', streaming = false }) {
  if (!text && !streaming) return null

  return (
    <div className="glass-card p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-6 h-6 rounded-md bg-amber-500/20 flex items-center justify-center">
          <Sparkles size={12} className="text-amber-400" />
        </div>
        <span className="text-sm font-semibold text-slate-300">{title}</span>
        <span className="text-xs text-slate-600 ml-auto">Powered by Claude</span>
      </div>

      {/* Content */}
      <div
        className="prose prose-invert prose-sm max-w-none
                   prose-p:text-slate-300 prose-p:leading-relaxed prose-p:my-2
                   prose-strong:text-amber-400 prose-strong:font-semibold
                   prose-ul:text-slate-300 prose-ul:my-2
                   prose-li:my-0.5
                   prose-h3:text-slate-100 prose-h3:font-bold prose-h3:text-base prose-h3:mt-4
                   prose-h4:text-slate-200 prose-h4:font-semibold"
      >
        {text ? (
          <ReactMarkdown>{text}</ReactMarkdown>
        ) : (
          <div className="flex items-center gap-2 text-slate-500">
            <span className="inline-block w-2 h-4 bg-amber-500/60 animate-pulse rounded-sm" />
            <span className="text-sm">Generating analysis…</span>
          </div>
        )}
      </div>

      {/* Streaming cursor */}
      {streaming && text && (
        <span className="inline-block w-2 h-4 bg-amber-500/60 animate-pulse rounded-sm ml-1 -mb-1" />
      )}
    </div>
  )
}
