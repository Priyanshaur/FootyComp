import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'

const RADAR_STATS = [
  { key: 'goals_p90', label: 'Goals' },
  { key: 'xg_p90', label: 'xG' },
  { key: 'prog_passes_p90', label: 'Prog Passes' },
  { key: 'pressures_p90', label: 'Pressing' },
  { key: 'tackles_p90', label: 'Defending' },
  { key: 'dribbles_p90', label: 'Dribbles' },
  { key: 'key_passes_p90', label: 'Key Passes' },
  { key: 'prog_carries_p90', label: 'Carries' },
]

function normalize(value, max) {
  if (value === null || value === undefined || !max || max === 0) return 0
  return Math.min(100, Math.round((value / max) * 100))
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card p-3 text-xs border border-white/10 shadow-xl">
      <p className="font-semibold text-slate-100 mb-1.5">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: p.color }} />
          <span className="text-slate-400">{p.name}:</span>
          <span className="font-semibold" style={{ color: p.color }}>{p.value}</span>
        </div>
      ))}
    </div>
  )
}

export default function PlayerRadarChart({ player1, player2 }) {
  if (!player1 || !player2) return null

  const data = RADAR_STATS.map(({ key, label }) => {
    const v1 = player1[key] || 0
    const v2 = player2[key] || 0
    const max = Math.max(v1, v2, 0.01)
    return {
      stat: label,
      [player1.name]: normalize(v1, max),
      [player2.name]: normalize(v2, max),
    }
  })

  return (
    <div className="glass-card p-6 animate-fade-in">
      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">
        Statistical Comparison Radar
      </h3>
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data} margin={{ top: 10, right: 40, bottom: 10, left: 40 }}>
          <PolarGrid stroke="rgba(255,255,255,0.07)" />
          <PolarAngleAxis
            dataKey="stat"
            tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'Inter', fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: '#475569', fontSize: 9 }}
            tickCount={5}
            axisLine={false}
          />
          <Radar
            name={player1.name}
            dataKey={player1.name}
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.15}
            strokeWidth={2.5}
            dot={{ fill: '#f59e0b', r: 3 }}
          />
          <Radar
            name={player2.name}
            dataKey={player2.name}
            stroke="#60a5fa"
            fill="#60a5fa"
            fillOpacity={0.15}
            strokeWidth={2.5}
            dot={{ fill: '#60a5fa', r: 3 }}
          />
          <Legend
            wrapperStyle={{
              paddingTop: '20px',
              fontSize: '13px',
              fontFamily: 'Inter',
              color: '#94a3b8',
            }}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
