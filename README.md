# FootIQ ⚽

> Football analytics platform — Player comparison, Team Fit Analysis, and AI-powered Cup predictions.

Built with **FBref data** · Powered by **Claude AI** · Deployed on **Vercel + Render**

---

## Features

| Feature | Description |
|---|---|
| **Player vs. Player** | Radar charts, stat tables, and AI summary across 14 dimensions |
| **Team Fit Analysis** | 0–100 Fit Score comparing a player's profile to a team's playing style |
| **Cup Predictor** | RAG chatbot: Claude predicts Champions League results using live stats |

## Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS → Vercel
- **Backend**: Python 3.11 + FastAPI → Render
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude Haiku (chatbot) + Claude Sonnet (analysis)
- **Data**: FBref via `soccerdata` library
- **Cron**: GitHub Actions (weekly scrape, Monday 02:00 UTC)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account (free) → [supabase.com](https://supabase.com)
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

### 1. Clone & set up environment

```bash
git clone https://github.com/yourusername/footiq.git
cd footiq
```

### 2. Set up the database

1. Go to your Supabase dashboard → SQL Editor
2. Paste and run the contents of `backend/db/schema.sql`
3. Copy your Project URL and `anon` key from Project Settings → API

### 3. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install chromium    # One-time: installs headless browser for soccerdata

# Create .env from template
copy .env.example .env
# Edit .env and fill in SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY
```

### 4. Run the first scrape (this takes ~10-20 mins for all leagues)

```bash
# From backend/ directory with venv activated
python -m scraper.fbref_players   # Scrapes all Big 5 league player stats
python -m scraper.fbref_teams     # Scrapes team-level stats
```

### 5. Start the backend

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 6. Frontend setup

```bash
cd frontend
npm install

# Create .env from template
copy .env.example .env
# Edit .env: VITE_API_URL=http://localhost:8000

npm run dev
# Frontend available at http://localhost:5173
```

---

## Project Structure

```
footiq/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── scraper/
│   │   ├── fbref_players.py     # Player stats scraper (soccerdata)
│   │   └── fbref_teams.py       # Team stats scraper
│   ├── models/
│   │   ├── fit_score.py         # Player-team fit scoring model
│   │   └── valuation.py         # Transfer value estimator
│   ├── chatbot/
│   │   └── predictor.py         # RAG chatbot (Claude Haiku + live stats)
│   ├── db/
│   │   ├── supabase_client.py   # Database helpers
│   │   └── schema.sql           # Supabase table definitions
│   └── routers/
│       ├── players.py
│       ├── teams.py
│       ├── compare.py
│       └── predict.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── PlayerSearch.jsx
│   │   │   ├── TeamSearch.jsx
│   │   │   ├── PlayerRadarChart.jsx
│   │   │   ├── StatTable.jsx
│   │   │   ├── FitScoreCard.jsx
│   │   │   └── AISummary.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Compare.jsx
│   │   │   ├── FitAnalysis.jsx
│   │   │   └── Predictor.jsx
│   │   ├── api/client.js
│   │   ├── App.jsx
│   │   └── index.css
│   ├── index.html
│   └── package.json
├── .github/
│   └── workflows/
│       └── scrape.yml           # Weekly FBref scraper cron job
└── README.md
```

---

## Deployment

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set root directory: `backend`
4. Build command: `pip install -r requirements.txt && playwright install chromium`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `SUPABASE_URL`, `SUPABASE_KEY`, `ANTHROPIC_API_KEY`, `FRONTEND_URL`

### Frontend → Vercel

1. Import your GitHub repo on [vercel.com](https://vercel.com)
2. Set root directory: `frontend`
3. Framework preset: **Vite**
4. Add environment variable: `VITE_API_URL=https://your-render-service.onrender.com`

### Weekly Scraper → GitHub Actions

Add these secrets to your GitHub repo (Settings → Secrets → Actions):
- `SUPABASE_URL`
- `SUPABASE_KEY`

The scraper runs automatically every Monday at 02:00 UTC. You can also trigger it manually from the Actions tab.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/players/search?q=name` | Search players by name |
| `GET` | `/players/{id}/stats` | Full stats for a player |
| `GET` | `/teams/search?q=name` | Search teams by name |
| `GET` | `/teams/{id}/profile` | Team style profile |
| `POST` | `/compare/players` | Compare two players + AI summary |
| `POST` | `/compare/fit` | Player-team fit score + valuation + AI |
| `POST` | `/predict/match` | Streaming Claude prediction |
| `GET` | `/docs` | Interactive API documentation |

---

## Data Sources

All statistics sourced from **[FBref.com](https://fbref.com)** via the `soccerdata` library.

Leagues covered: Premier League · La Liga · Bundesliga · Serie A · Ligue 1

Seasons: 2023/24 · 2024/25

---

*FootIQ — Built with FBref data · Powered by Claude*
