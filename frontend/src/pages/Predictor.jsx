import { useState, useRef, useCallback } from 'react'
import { Sparkles, Loader2, AlertCircle, Send, RefreshCw } from 'lucide-react'
import TeamSearch from '../components/TeamSearch'
import AISummary from '../components/AISummary'
import { getPredictStreamUrl } from '../api/client'

const EXAMPLE_PROMPTS = [
  'Who wins Real Madrid vs Man City based on current form?',
  'Predict Bayern Munich vs Arsenal in the Champions League',
  'How would PSG vs Inter Milan go this season?',
  'Compare Liverpool vs Atletico Madrid knockout chances',
]

export default function Predictor() {
  const [team1, setTeam1] = useState(null)
  const [team2, setTeam2] = useState(null)
  const [question, setQuestion] = useState('')
  const [streamedText, setStreamedText] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState(null)
  const esRef = useRef(null)

  const canPredict = Boolean((team1 && team2) || question.trim().length > 5)

  const handlePredict = useCallback(async () => {
    if (!canPredict || streaming) return

    // Close any existing stream
    if (esRef.current) esRef.current.close()

    setStreamedText('')
    setStreaming(true)
    setDone(false)
    setError(null)

    try {
      const streamUrl = getPredictStreamUrl()
      const params = new URLSearchParams()
      if (team1) params.set('team1_id', team1.id)
      if (team2) params.set('team2_id', team2.id)
      if (question.trim()) params.set('question', question.trim())

      const url = `${streamUrl}?${params.toString()}`
      const es = new EventSource(url)
      esRef.current = es

      es.onmessage = (event) => {
        if (event.data === '[DONE]') {
          es.close()
          setStreaming(false)
          setDone(true)
          return
        }
        try {
          const parsed = JSON.parse(event.data)
          const chunk = parsed.text || parsed.chunk || parsed.content || ''
          setStreamedText((prev) => prev + chunk)
        } catch {
          // raw text chunk
          setStreamedText((prev) => prev + event.data)
        }
      }

      es.onerror = () => {
        es.close()
        setStreaming(false)
        setDone(true)
      }
    } catch (e) {
      setError('Prediction failed. Is the backend running?')
      setStreaming(false)
    }
  }, [canPredict, streaming, team1, team2, question])

  const handleReset = () => {
    if (esRef.current) esRef.current.close()
    setStreamedText('')
    setStreaming(false)
    setDone(false)
    setError(null)
  }

  return (
    <div className="pt-24 pb-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-10 animate-fade-in">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 flex items-center justify-center">
              <Sparkles size={20} className="text-purple-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100">Match Predictor</h1>
              <p className="text-slate-500 text-sm mt-0.5">
                AI predictions grounded in real team statistics — not historical reputation
              </p>
            </div>
          </div>
        </div>

        {/* Input card */}
        <div className="glass-card p-6 mb-8 animate-slide-up space-y-6">
          {/* Team selectors */}
          <div className="grid md:grid-cols-2 gap-6">
            <TeamSearch
              id="predict-team1-search"
              label="Home Team"
              onSelect={setTeam1}
              selectedTeam={team1}
            />
            <TeamSearch
              id="predict-team2-search"
              label="Away Team"
              onSelect={setTeam2}
              selectedTeam={team2}
            />
          </div>

          {/* VS divider */}
          {(team1 || team2) && (
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-white/[0.06]" />
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">vs</div>
              <div className="flex-1 h-px bg-white/[0.06]" />
            </div>
          )}

          {/* Custom question */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Your Question <span className="text-slate-600 font-normal">(optional — overrides team selection)</span>
            </label>
            <div className="relative">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Who wins Real Madrid vs Man City based on current form?"
                rows={3}
                className="search-input resize-none pr-12 leading-relaxed"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handlePredict()
                }}
              />
              <div className="absolute bottom-3 right-3 text-xs text-slate-600">
                ⌘↵
              </div>
            </div>
          </div>

          {/* Example prompts */}
          <div>
            <div className="text-xs text-slate-500 mb-2">Try an example:</div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => setQuestion(p)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-navy-700 hover:bg-navy-600
                            text-slate-400 hover:text-slate-200 border border-white/[0.06]
                            transition-all duration-150"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="flex gap-3 justify-end">
            {(streamedText || done) && (
              <button onClick={handleReset} className="btn-ghost flex items-center gap-2 text-sm">
                <RefreshCw size={15} />
                New Prediction
              </button>
            )}
            <button
              id="btn-predict"
              onClick={handlePredict}
              disabled={!canPredict || streaming}
              className="btn-primary flex items-center gap-2
                        disabled:opacity-40 disabled:cursor-not-allowed
                        disabled:transform-none disabled:shadow-none"
            >
              {streaming ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
              {streaming ? 'Predicting…' : 'Predict Match'}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="glass-card p-4 mb-8 flex items-start gap-3 border border-red-500/20 bg-red-500/5">
            <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
            <span className="text-red-300 text-sm">{error}</span>
          </div>
        )}

        {/* Streamed output */}
        {(streamedText || streaming) && (
          <AISummary
            text={streamedText}
            title="Match Prediction"
            streaming={streaming && !done}
          />
        )}

        {/* Empty state */}
        {!streamedText && !streaming && !error && (
          <div className="text-center py-20 text-slate-600">
            <Sparkles size={48} className="mx-auto mb-4 opacity-25" />
            <p className="text-lg font-medium">Select two teams or type your question.</p>
            <p className="text-sm mt-1 max-w-sm mx-auto">
              FootIQ fetches real current-season statistics before generating the prediction
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
