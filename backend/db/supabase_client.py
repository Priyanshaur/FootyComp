import os
from typing import Any
from supabase import create_client  # type: ignore[import]
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase: Any = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Players ────────────────────────────────────────────────────────────────────

def search_players(query: str, limit: int = 10) -> list:
    """Search players by name (case-insensitive partial match)."""
    response = supabase.table("players") \
        .select("id, name, team, league, season, position, age") \
        .ilike("name", f"%{query}%") \
        .limit(limit) \
        .execute()
    return response.data


def get_player_by_id(player_id: str) -> dict | None:
    """Get full stats for a single player."""
    response = supabase.table("players") \
        .select("*") \
        .eq("id", player_id) \
        .single() \
        .execute()
    return response.data


def get_players_by_team(team: str, season: str = "2024-2025") -> list:
    """Get all players for a team in a given season."""
    response = supabase.table("players") \
        .select("*") \
        .ilike("team", f"%{team}%") \
        .eq("season", season) \
        .execute()
    return response.data


def upsert_player(player_data: dict) -> None:
    """Insert or update a player row (used by the scraper)."""
    supabase.table("players") \
        .upsert(player_data, on_conflict="id") \
        .execute()


def upsert_players_bulk(players: list[dict]) -> None:
    """Bulk insert/update players (used by the scraper for efficiency)."""
    if not players:
        return
    # Supabase handles up to 1000 rows per request
    chunk_size = 500
    for i in range(0, len(players), chunk_size):
        chunk = players[i:i + chunk_size]
        supabase.table("players") \
            .upsert(chunk, on_conflict="id") \
            .execute()
    print(f"Upserted {len(players)} players")


# ── Teams ──────────────────────────────────────────────────────────────────────

def search_teams(query: str, limit: int = 10) -> list:
    """Search teams by name."""
    response = supabase.table("teams") \
        .select("id, name, league, season") \
        .ilike("name", f"%{query}%") \
        .limit(limit) \
        .execute()
    return response.data


def get_team_by_id(team_id: str) -> dict | None:
    """Get full style profile for a team."""
    response = supabase.table("teams") \
        .select("*") \
        .eq("id", team_id) \
        .single() \
        .execute()
    return response.data


def get_team_by_name(name: str, season: str = "2024-2025") -> dict | None:
    """Get a team by approximate name match."""
    response = supabase.table("teams") \
        .select("*") \
        .ilike("name", f"%{name}%") \
        .eq("season", season) \
        .limit(1) \
        .execute()
    return response.data[0] if response.data else None


def upsert_team(team_data: dict) -> None:
    """Insert or update a team row."""
    supabase.table("teams") \
        .upsert(team_data, on_conflict="id") \
        .execute()


def upsert_teams_bulk(teams: list[dict]) -> None:
    """Bulk insert/update teams."""
    if not teams:
        return
    supabase.table("teams") \
        .upsert(teams, on_conflict="id") \
        .execute()
    print(f"Upserted {len(teams)} teams")


# ── Fit Scores ─────────────────────────────────────────────────────────────────

def get_cached_fit_score(player_id: str, team_id: str, season: str = "2024-2025") -> dict | None:
    """Check if a fit score has already been calculated and cached."""
    response = supabase.table("fit_scores") \
        .select("*") \
        .eq("player_id", player_id) \
        .eq("team_id", team_id) \
        .eq("season", season) \
        .limit(1) \
        .execute()
    return response.data[0] if response.data else None


def save_fit_score(fit_data: dict) -> None:
    """Cache a fit score result."""
    supabase.table("fit_scores") \
        .upsert(fit_data, on_conflict="player_id,team_id,season") \
        .execute()


# ── Match Predictions ──────────────────────────────────────────────────────────

def get_cached_prediction(home_team: str, away_team: str, competition: str) -> dict | None:
    """
    Check if a prediction already exists for this matchup.
    Only returns predictions made in the last 7 days (stale predictions are useless).
    """
    response = supabase.table("match_predictions") \
        .select("*") \
        .eq("home_team", home_team) \
        .eq("away_team", away_team) \
        .eq("competition", competition) \
        .gte("created_at", "NOW() - INTERVAL '7 days'") \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    return response.data[0] if response.data else None


def save_prediction(prediction_data: dict) -> None:
    """Save a new match prediction."""
    supabase.table("match_predictions") \
        .insert(prediction_data) \
        .execute()


# ── Health Check ───────────────────────────────────────────────────────────────

def health_check() -> bool:
    """Verify the database connection is working."""
    try:
        supabase.table("players").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False