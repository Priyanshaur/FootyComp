import { useState, useEffect, useRef } from 'react'
import { Search, User, Loader2 } from 'lucide-react'
import { searchPlayers } from '../api/client'

const LEAGUE_FLAGS = {
  'ENG-Premier League': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'ESP-La Liga': '🇪🇸',
  'GER-Bundesliga': '🇩🇪',
  'ITA-Serie A': '🇮🇹',
  'FRA-Ligue 1': '🇫🇷',
}

const POSITION_COLORS = {
  FWD: 'bg-red-500/20 text-red-300',
  MID: 'bg-blue-500/20 text-blue-300',
  DEF: 'bg-green-500/20 text-green-300',
  GK: 'bg-yellow-500/20 text-yellow-300',
}

export default function PlayerSearch({ id, label, onSelect, selectedPlayer }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const debounceRef = useRef(null)
  const wrapperRef = useRef(null)

  // Pre-fill query when selectedPlayer changes externally
  useEffect(() => {
    if (selectedPlayer) {
      setQuery(selectedPlayer.name)
    }
  }, [selectedPlayer])

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      setOpen(false)
      return
    }
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await searchPlayers(query)
        setResults(res.data.players || [])
        setOpen(true)
      } catch (e) {
        console.error('Search failed:', e)
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [query])

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSelect = (player) => {
    onSelect(player)
    setQuery(player.name)
    setOpen(false)
  }

  const handleChange = (e) => {
    setQuery(e.target.value)
    if (!e.target.value) onSelect(null)
  }

  return (
    <div ref={wrapperRef} className="relative w-full">
      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
        {label}
      </label>
      <div className="relative">
        <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        <input
          id={id}
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="Search player name..."
          className="search-input pl-10 pr-10"
          autoComplete="off"
        />
        {loading && (
          <Loader2
            size={16}
            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-amber-500 animate-spin pointer-events-none"
          />
        )}
      </div>

      {/* Dropdown results */}
      {open && results.length > 0 && (
        <div
          className="absolute top-full left-0 right-0 mt-2 glass-card overflow-hidden z-50
                     border border-white/10 shadow-2xl max-h-72 overflow-y-auto animate-fade-in"
        >
          {results.map((player) => (
            <button
              key={player.id}
              onClick={() => handleSelect(player)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5
                        transition-colors duration-150 text-left border-b border-white/5 last:border-0"
            >
              <div className="w-8 h-8 rounded-full bg-navy-700 flex items-center justify-center flex-shrink-0">
                <User size={14} className="text-slate-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-slate-100 truncate">{player.name}</div>
                <div className="text-xs text-slate-500">
                  {LEAGUE_FLAGS[player.league] || '🌍'} {player.team}
                </div>
              </div>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded-md flex-shrink-0
                           ${POSITION_COLORS[player.position_group] || 'bg-slate-700 text-slate-300'}`}
              >
                {player.position_group}
              </span>
            </button>
          ))}
        </div>
      )}

      {open && results.length === 0 && !loading && query.length >= 2 && (
        <div
          className="absolute top-full left-0 right-0 mt-2 glass-card p-4 text-center
                     text-slate-500 text-sm animate-fade-in z-50"
        >
          No players found for &quot;{query}&quot;
        </div>
      )}
    </div>
  )
}
