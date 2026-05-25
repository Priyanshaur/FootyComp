import { useState } from 'react'
import { Target, Loader2, AlertCircle, DollarSign, TrendingUp } from 'lucide-react'
import PlayerSearch from '../components/PlayerSearch'
import TeamSearch from '../components/TeamSearch'
import FitScoreCard from '../components/FitScoreCard'
import AISummary from '../components/AISummary'
import { fitAnalysis } from '../api/client'

export default function FitAnalysis() {
  const [player, setPlayer] = useState(null)
  const [team, setTeam] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const canAnalyse = Boolean(player && team)

  const handleAnalyse = async () => {
    if (!canAnalyse) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fitAnalysis(player.id, team.id)
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Analysis failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-10 animate-fade-in">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center">
              <Target size={20} className="text-amber-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100">Team Fit Analysis</h1>
              <p className="text-slate-500 text-sm mt-0.5">
                Quantify how well a player fits a team&apos;s playing style with a 0–100 score
              </p>
            </div>
          </div>
        </div>

        {/* Search card */}
        <div className="glass-card p-6 mb-8 animate-slide-up">
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <PlayerSearch
              id="fit-player-search"
              label="Player"
              onSelect={setPlayer}
              selectedPlayer={player}
            />
            <TeamSearch
              id="fit-team-search"
              label="Target Team"
              onSelect={setTeam}
              selectedTeam={team}
            />
          </div>
          <div className="flex justify-center">
            <button
              id="btn-analyse-fit"
              onClick={handleAnalyse}
              disabled={!canAnalyse || loading}
              className="btn-primary flex items-center gap-2
                        disabled:opacity-40 disabled:cursor-not-allowed
                        disabled:transform-none disabled:shadow-none"
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Target size={18} />
              )}
              {loading ? 'Analysing Fit…' : 'Analyse Fit'}
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

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-fade-in">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Fit score card */}
              <div className="lg:col-span-1">
                <FitScoreCard
                  score={result.fit_score}
                  categoryScores={result.category_scores}
                  playerName={player?.name}
                  teamName={team?.name}
                />
              </div>

              {/* Right panel: transfer value + style notes */}
              <div className="lg:col-span-2 space-y-4">
                {result.estimated_value && (
                  <div className="glass-card p-5 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
                      <DollarSign size={20} className="text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-0.5">
                        Estimated Transfer Value
                      </div>
                      <div className="text-2xl font-black text-emerald-400">
                        {result.estimated_value}
                      </div>
                    </div>
                  </div>
                )}

                {result.style_notes && (
                  <div className="glass-card p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp size={16} className="text-amber-400" />
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        Playing Style Notes
                      </span>
                    </div>
                    <ul className="space-y-2">
                      {result.style_notes.map((note, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <span className="text-amber-500 mt-0.5 flex-shrink-0">›</span>
                          {note}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Stat deltas if present */}
                {result.key_stats && (
                  <div className="glass-card p-5">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                      Key Stats vs. Team Average
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(result.key_stats).map(([label, { player: pv, team: tv, better }]) => (
                        <div
                          key={label}
                          className="bg-navy-700/40 rounded-xl p-3 border border-white/[0.04]"
                        >
                          <div className="text-xs text-slate-500 mb-1">{label}</div>
                          <div className="flex items-end gap-2">
                            <span className={`text-lg font-black ${better ? 'text-emerald-400' : 'text-red-400'}`}>
                              {typeof pv === 'number' ? pv.toFixed(2) : pv}
                            </span>
                            <span className="text-xs text-slate-500 mb-0.5">
                              vs {typeof tv === 'number' ? tv.toFixed(2) : tv}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <AISummary text={result.ai_summary} title="AI Fit Analysis" />
          </div>
        )}

        {/* Empty state */}
        {!result && !loading && !error && (
          <div className="text-center py-24 text-slate-600">
            <Target size={48} className="mx-auto mb-4 opacity-30" />
            <p className="text-lg font-medium">Select a player and target team above.</p>
            <p className="text-sm mt-1">Get a 0–100 Fit Score with AI-backed reasoning</p>
          </div>
        )}
      </div>
    </div>
  )
}
