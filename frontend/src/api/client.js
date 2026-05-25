import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging in dev
api.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data || '')
  }
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('[API Error]', error.response?.status, error.response?.data || error.message)
    }
    return Promise.reject(error)
  }
)

// ─── Players ────────────────────────────────────────────────────────────────
export const searchPlayers = (query, league, position) =>
  api.get('/players/search', { params: { q: query, league, position } })

export const getPlayerStats = (playerId, season) =>
  api.get(`/players/${playerId}/stats`, { params: { season } })

// ─── Teams ───────────────────────────────────────────────────────────────────
export const searchTeams = (query, league) =>
  api.get('/teams/search', { params: { q: query, league } })

export const getTeamProfile = (teamId, season) =>
  api.get(`/teams/${teamId}/profile`, { params: { season } })

// ─── Compare ─────────────────────────────────────────────────────────────────
export const comparePlayers = (player1Id, player2Id, season) =>
  api.post('/compare/players', { player1_id: player1Id, player2_id: player2Id, season })

export const fitAnalysis = (playerId, teamId, season) =>
  api.post('/compare/fit', { player_id: playerId, team_id: teamId, season })

// ─── Predict ─────────────────────────────────────────────────────────────────
// Returns URL for EventSource (streaming SSE)
export const getPredictStreamUrl = () => `${BASE_URL}/predict/match`

export const getPredictContext = (team1Id, team2Id) =>
  api.get('/predict/context', { params: { team1_id: team1Id, team2_id: team2Id } })

export default api
