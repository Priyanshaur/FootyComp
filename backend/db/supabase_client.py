"""
Supabase database client for FootIQ.
Provides helper functions for reading/writing player and team data.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Optional[Client] = None


def get_client() -> Client:
    """Return singleton Supabase client."""
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env"
            )
        _client = create_client(url, key)
    return _client


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------

def search_players(query: str, league: Optional[str] = None, position_group: Optional[str] = None, limit: int = 20):
    """Search players by name (case-insensitive partial match)."""
    db = get_client()
    q = (
        db.table("players")
        .select("id,name,team,league,position,position_group,age,season")
        .ilike("name", f"%{query}%")
    )
    if league:
        q = q.eq("league", league)
    if position_group:
        q = q.eq("position_group", position_group)
    q = q.order("name").limit(limit)
    return q.execute().data


def get_player_stats(player_id: str, season: Optional[str] = None):
    """Return full stats for a player. If season omitted, returns latest."""
    db = get_client()
    q = db.table("players").select("*").eq("id", player_id)
    if season:
        q = q.eq("season", season)
    else:
        q = q.order("season", desc=True).limit(1)
    result = q.execute().data
    return result[0] if result else None


def upsert_players(records: list[dict]):
    """Upsert a list of player records. Uses player id + season as key."""
    db = get_client()
    return db.table("players").upsert(records, on_conflict="id,season").execute()


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def search_teams(query: str, league: Optional[str] = None, limit: int = 20):
    """Search teams by name."""
    db = get_client()
    q = (
        db.table("teams")
        .select("id,name,league,season")
        .ilike("name", f"%{query}%")
    )
    if league:
        q = q.eq("league", league)
    q = q.order("name").limit(limit)
    return q.execute().data


def get_team_profile(team_id: str, season: Optional[str] = None):
    """Return full style profile for a team."""
    db = get_client()
    q = db.table("teams").select("*").eq("id", team_id)
    if season:
        q = q.eq("season", season)
    else:
        q = q.order("season", desc=True).limit(1)
    result = q.execute().data
    return result[0] if result else None


def upsert_teams(records: list[dict]):
    """Upsert a list of team records."""
    db = get_client()
    return db.table("teams").upsert(records, on_conflict="id,season").execute()


def get_teams_by_ids(team_ids: list[str]):
    """Return team profiles for a list of IDs (used by chatbot)."""
    db = get_client()
    return db.table("teams").select("*").in_("id", team_ids).execute().data
