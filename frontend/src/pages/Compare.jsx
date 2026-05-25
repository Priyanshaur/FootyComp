import { useState } from 'react'
import { GitCompare, Loader2, AlertCircle } from 'lucide-react'
import PlayerSearch from '../components/PlayerSearch'
import PlayerRadarChart from '../components/PlayerRadarChart'
import StatTable from '../components/StatTable'
import AISummary from '../components/AISummary'
import { comparePlayers } from '../api/client'

export default function Compare() {
  const [player1, setPlayer1] = useState(null)
  const [player2, setPlayer2] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const canCompare = player1 && player2 && player1.id !== player2.id
  const samePlayer = player1 && player2 && player1.id === player2.id

  const handleCompare = async () => {
    if (!canCompare) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await comparePlayers(player1.id, player2.id)
      setResult(res.data)
    } catch (e) {
      setError(
        e.response?.data?.detail || 'Failed to compare players. Is the backend running?'
      )
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
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 flex items-center justify-center">
              <GitCompare size={20} className="text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-100">Player Comparison</h1>
              <p className="text-slate-500 text-sm mt-0.5">
                Side-by-side analysis across multiple statistical dimensions
              </p>
            </div>
          </div>
        </div>

        {/* Search card */}
        <div className="glass-card p-6 mb-8 animate-slide-up">
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <PlayerSearch
              id="player1-search"
              label="Player 1"
              onSelect={setPlayer1}
              selectedPlayer={player1}
            />
            <PlayerSearch
              id="player2-search"
              label="Player 2"
              onSelect={setPlayer2}
              selectedPlayer={player2}
            />
          </div>

          {samePlayer && (
            <p className="text-amber-400 text-sm text-center mb-4">
              Please select two <em>different</em> players to compare.
            </p>
          )}

          <div className="flex justify-center">
            <button
              id="btn-compare"
              onClick={handleCompare}
              disabled={!canCompare || loading}
              className="btn-primary flex items-center gap-2
                        disabled:opacity-40 disabled:cursor-not-allowed
                        disabled:transform-none disabled:shadow-none"
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <GitCompare size={18} />
              )}
              {loading ? 'Analysing…' : 'Compare Players'}
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
            {/* Player name headers */}
            <div className="grid md:grid-cols-2 gap-4">
              <PlayerCard player={result.player1} color="#f59e0b" />
              <PlayerCard player={result.player2} color="#60a5fa" />
            </div>

            <PlayerRadarChart player1={result.player1} player2={result.player2} />
            <StatTable
              player1={result.player1}
              player2={result.player2}
              deltas={result.stat_deltas}
            />
            <AISummary text={result.ai_summary} title="AI Comparison Analysis" />
          </div>
        )}

        {/* Empty state prompt */}
        {!result && !loading && !error && (
          <div className="text-center py-24 text-slate-600">
            <GitCompare size={48} className="mx-auto mb-4 opacity-30" />
            <p className="text-lg font-medium">Select two players above to begin.</p>
            <p className="text-sm mt-1">Search by name — any player from the Big 5 leagues</p>
          </div>
        )}
      </div>
    </div>
  )
}

function PlayerCard({ player, color }) {
  if (!player) return null
  return (
    <div
      className="glass-card p-4 flex items-center gap-4 transition-all duration-300"
      style={{ borderColor: `${color}25` }}
    >
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center font-black text-xl flex-shrink-0"
        style={{ backgroundColor: `${color}15`, color }}
      >
        {player.name?.[0] || '?'}
      </div>
      <div className="min-w-0">
        <div className="font-bold text-slate-100 text-lg truncate">{player.name}</div>
        <div className="text-sm text-slate-500 truncate">
          {player.team} · {player.position_group}
          {player.season && ` · ${player.season}`}
        </div>
      </div>
    </div>
  )
}
