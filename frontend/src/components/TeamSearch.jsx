import { useState, useEffect, useRef } from 'react'
import { Search, Shield, Loader2 } from 'lucide-react'
import { searchTeams } from '../api/client'

const LEAGUE_FLAGS = {
  'ENG-Premier League': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'ESP-La Liga': '🇪🇸',
  'GER-Bundesliga': '🇩🇪',
  'ITA-Serie A': '🇮🇹',
  'FRA-Ligue 1': '🇫🇷',
}

export default function TeamSearch({ id, label, onSelect, selectedTeam }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const debounceRef = useRef(null)
  const wrapperRef = useRef(null)

  useEffect(() => {
    if (selectedTeam) setQuery(selectedTeam.name)
  }, [selectedTeam])

  useEffect(() => {
    if (query.length < 2) { setResults([]); setOpen(false); return }
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await searchTeams(query)
        setResults(res.data.teams || [])
        setOpen(true)
      } catch (e) {
        console.error('Team search failed:', e)
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [query])

  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSelect = (team) => {
    onSelect(team)
    setQuery(team.name)
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
          placeholder="Search team name..."
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

      {open && results.length > 0 && (
        <div
          className="absolute top-full left-0 right-0 mt-2 glass-card overflow-hidden z-50
                     border border-white/10 shadow-2xl max-h-64 overflow-y-auto animate-fade-in"
        >
          {results.map((team) => (
            <button
              key={team.id}
              onClick={() => handleSelect(team)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5
                        transition-colors border-b border-white/5 last:border-0 text-left"
            >
              <div className="w-8 h-8 rounded-full bg-navy-700 flex items-center justify-center flex-shrink-0">
                <Shield size={14} className="text-amber-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-slate-100 truncate">{team.name}</div>
                <div className="text-xs text-slate-500">
                  {LEAGUE_FLAGS[team.league] || '🌍'} {team.league}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {open && results.length === 0 && !loading && query.length >= 2 && (
        <div
          className="absolute top-full left-0 right-0 mt-2 glass-card p-4 text-center
                     text-slate-500 text-sm animate-fade-in z-50"
        >
          No teams found for &quot;{query}&quot;
        </div>
      )}
    </div>
  )
}
