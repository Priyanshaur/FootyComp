import { useEffect, useState } from 'react'

const SCORE_CONFIGS = [
  { min: 0, max: 40, color: '#ef4444', label: 'Poor Fit', bg: 'rgba(239,68,68,0.1)' },
  { min: 40, max: 60, color: '#f59e0b', label: 'Moderate Fit', bg: 'rgba(245,158,11,0.1)' },
  { min: 60, max: 80, color: '#10b981', label: 'Good Fit', bg: 'rgba(16,185,129,0.1)' },
  { min: 80, max: 101, color: '#34d399', label: 'Excellent Fit', bg: 'rgba(52,211,153,0.1)' },
]

function getScoreConfig(score) {
  return SCORE_CONFIGS.find((c) => score >= c.min && score < c.max) || SCORE_CONFIGS[0]
}

const RADIUS = 48
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function FitScoreCard({ score, categoryScores, playerName, teamName }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const config = getScoreConfig(score || 0)

  useEffect(() => {
    if (!score) return
    let start = 0
    const end = score
    const duration = 1200
    const steps = 60
    const increment = end / steps
    const timer = setInterval(() => {
      start += increment
      if (start >= end) {
        setAnimatedScore(end)
        clearInterval(timer)
      } else {
        setAnimatedScore(Math.round(start))
      }
    }, duration / steps)
    return () => clearInterval(timer)
  }, [score])

  const offset = CIRCUMFERENCE - (animatedScore / 100) * CIRCUMFERENCE

  return (
    <div className="glass-card p-6 animate-slide-up h-full">
      <div className="flex flex-col items-center gap-6">
        {/* Circular score gauge */}
        <div className="relative" title={`Fit Score: ${score}/100`}>
          <svg width="160" height="160" className="-rotate-90" style={{ overflow: 'visible' }}>
            {/* Track */}
            <circle
              cx="80" cy="80" r={RADIUS}
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="12"
            />
            {/* Progress arc */}
            <circle
              cx="80" cy="80" r={RADIUS}
              fill="none"
              stroke={config.color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={offset}
              style={{
                transition: 'stroke-dashoffset 0.04s ease-out',
                filter: `drop-shadow(0 0 10px ${config.color}60)`,
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-5xl font-black tabular-nums" style={{ color: config.color }}>
              {animatedScore}
            </span>
            <span className="text-xs text-slate-500 font-medium mt-0.5">/ 100</span>
          </div>
        </div>

        {/* Label */}
        <div className="text-center">
          <div
            className="text-lg font-bold px-4 py-1 rounded-full"
            style={{ color: config.color, backgroundColor: config.bg }}
          >
            {config.label}
          </div>
          {playerName && teamName && (
            <div className="text-sm text-slate-500 mt-2">
              <span className="text-slate-300 font-medium">{playerName}</span>
              {' → '}
              <span className="text-slate-300 font-medium">{teamName}</span>
            </div>
          )}
        </div>

        {/* Category breakdown */}
        {categoryScores && Object.keys(categoryScores).length > 0 && (
          <div className="w-full space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider border-t border-white/[0.06] pt-4">
              Category Breakdown
            </div>
            {Object.entries(categoryScores).map(([cat, val]) => {
              const catConfig = getScoreConfig(Number(val))
              return (
                <div key={cat}>
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs text-slate-400">{cat}</span>
                    <span className="text-xs font-bold tabular-nums" style={{ color: catConfig.color }}>
                      {val}
                    </span>
                  </div>
                  <div className="h-1.5 bg-navy-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: `${Math.min(100, Number(val))}%`,
                        backgroundColor: catConfig.color,
                        boxShadow: `0 0 8px ${catConfig.color}50`,
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
