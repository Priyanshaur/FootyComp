import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const STAT_LABELS = {
  goals_p90: 'Goals / 90',
  assists_p90: 'Assists / 90',
  xg_p90: 'xG / 90',
  xag_p90: 'xAG / 90',
  npxg_p90: 'npxG / 90',
  prog_passes_p90: 'Progressive Passes / 90',
  key_passes_p90: 'Key Passes / 90',
  pass_completion: 'Pass Completion %',
  prog_carries_p90: 'Progressive Carries / 90',
  dribbles_p90: 'Dribbles / 90',
  tackles_p90: 'Tackles / 90',
  interceptions_p90: 'Interceptions / 90',
  pressures_p90: 'Pressures / 90',
  aerial_won_pct: 'Aerial Duels Won %',
}

const CATEGORIES = {
  Attacking: ['goals_p90', 'xg_p90', 'npxg_p90', 'xag_p90', 'assists_p90', 'key_passes_p90'],
  Possession: ['prog_passes_p90', 'pass_completion', 'prog_carries_p90', 'dribbles_p90'],
  'Pressing & Defence': ['pressures_p90', 'tackles_p90', 'interceptions_p90', 'aerial_won_pct'],
}

export default function StatTable({ player1, player2, deltas }) {
  if (!player1 || !player2 || !deltas) return null

  const fmt = (v) =>
    v === null || v === undefined ? '—' : typeof v === 'number' ? v.toFixed(2) : String(v)

  return (
    <div className="glass-card overflow-hidden animate-slide-up">
      {/* Player header row */}
      <div className="flex items-center border-b border-white/[0.06] px-4 py-3 bg-navy-700/40">
        <div className="flex-1 text-right">
          <span className="text-sm font-bold text-amber-400 truncate">{player1.name}</span>
        </div>
        <div className="w-48 text-center">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Stat</span>
        </div>
        <div className="flex-1 text-left">
          <span className="text-sm font-bold text-blue-400 truncate">{player2.name}</span>
        </div>
      </div>

      {Object.entries(CATEGORIES).map(([category, stats]) => (
        <div key={category}>
          {/* Category header */}
          <div className="px-4 py-2.5 bg-navy-700/30 border-b border-white/[0.04]">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{category}</span>
          </div>

          {stats.map((stat) => {
            const d = deltas[stat]
            if (!d) return null
            const p1Better = d.better === 'player1'
            const tied = d.delta === 0 || d.better === 'tied'

            return (
              <div
                key={stat}
                className="flex items-center px-4 py-3 border-b border-white/[0.035] last:border-0
                          hover:bg-white/[0.02] transition-colors duration-150 group"
              >
                {/* Player 1 value */}
                <div className="flex-1 text-right pr-3">
                  <span
                    className={`font-mono text-sm font-semibold transition-colors ${
                      p1Better && !tied ? 'text-emerald-400' : 'text-slate-400'
                    }`}
                  >
                    {fmt(d.player1)}
                  </span>
                </div>

                {/* Stat name + trend indicator */}
                <div className="w-48 text-center px-2">
                  <div className="text-xs text-slate-500 group-hover:text-slate-400 transition-colors">
                    {STAT_LABELS[stat] || stat}
                  </div>
                  <div className="flex items-center justify-center mt-0.5 gap-1">
                    {tied ? (
                      <Minus size={10} className="text-slate-600" />
                    ) : p1Better ? (
                      <TrendingUp size={10} className="text-amber-500" />
                    ) : (
                      <TrendingDown size={10} className="text-blue-400" />
                    )}
                  </div>
                </div>

                {/* Player 2 value */}
                <div className="flex-1 text-left pl-3">
                  <span
                    className={`font-mono text-sm font-semibold transition-colors ${
                      !p1Better && !tied ? 'text-emerald-400' : 'text-slate-400'
                    }`}
                  >
                    {fmt(d.player2)}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
