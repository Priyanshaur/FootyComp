from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from db.supabase_client import search_teams, get_team_profile

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=2, description="Team name search query"),
    league: Optional[str] = Query(None, description="Filter by league name"),
):
    """
    Search teams by name. Returns list for team selector dropdowns.
    """
    results = search_teams(query=q, league=league)
    return {"teams": results, "count": len(results)}


@router.get("/{team_id}/profile")
async def get_profile(
    team_id: str,
    season: Optional[str] = Query(None, description="Season code e.g. '2425'"),
):
    """
    Get the full style profile for a team. Used by the fit analysis page.
    """
    team = get_team_profile(team_id, season=season)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
    return team
