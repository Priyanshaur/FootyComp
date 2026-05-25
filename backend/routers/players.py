from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from db.supabase_client import search_players, get_player_stats

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=2, description="Player name search query"),
    league: Optional[str] = Query(None, description="Filter by league name"),
    position: Optional[str] = Query(None, description="Filter by position group: GK/DEF/MID/FWD"),
):
    """
    Search for players by name. Returns basic info for search UI dropdowns.
    """
    results = search_players(query=q, league=league, position_group=position)
    return {"players": results, "count": len(results)}


@router.get("/{player_id}/stats")
async def get_stats(
    player_id: str,
    season: Optional[str] = Query(None, description="Season code e.g. '2425'. Defaults to latest."),
):
    """
    Get full stats for a player. Used by the comparison and fit analysis pages.
    """
    player = get_player_stats(player_id, season=season)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")
    return player
