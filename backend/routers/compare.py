"""
Player comparison and player-team fit analysis endpoints.
Uses Claude Sonnet for high-quality one-shot AI explanations.
"""

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import anthropic
from db.supabase_client import get_player_stats, get_team_profile
from models.fit_score import compute_fit_score
from models.valuation import estimate_value

router = APIRouter(prefix="/compare", tags=["Compare"])
log = logging.getLogger(__name__)

CLIENT = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
SONNET_MODEL = "claude-3-5-sonnet-20241022"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ComparePlayersRequest(BaseModel):
    player1_id: str
    player2_id: str
    season: Optional[str] = None


class FitAnalysisRequest(BaseModel):
    player_id: str
    team_id: str
    season: Optional[str] = None


# ---------------------------------------------------------------------------
# Player vs Player
# ---------------------------------------------------------------------------

@router.post("/players")
async def compare_players(req: ComparePlayersRequest):
    """
    Compare two players side-by-side. Returns stat deltas and an AI summary.
    """
    p1 = get_player_stats(req.player1_id, season=req.season)
    p2 = get_player_stats(req.player2_id, season=req.season)

    if not p1:
        raise HTTPException(404, detail=f"Player 1 not found: {req.player1_id}")
    if not p2:
        raise HTTPException(404, detail=f"Player 2 not found: {req.player2_id}")

    # Build stat delta dict
    stat_cols = [
        "goals_p90", "assists_p90", "xg_p90", "xag_p90", "npxg_p90",
        "prog_passes_p90", "key_passes_p90", "pass_completion",
        "prog_carries_p90", "dribbles_p90",
        "tackles_p90", "interceptions_p90",
        "pressures_p90", "aerial_won_pct",
    ]
    deltas = {}
    for col in stat_cols:
        v1 = p1.get(col)
        v2 = p2.get(col)
        deltas[col] = {
            "player1": v1,
            "player2": v2,
            "delta": round((v1 or 0) - (v2 or 0), 4),
            "better": "player1" if (v1 or 0) >= (v2 or 0) else "player2",
        }

    # Build prompt for Claude
    prompt = f"""You are FootIQ, a football analytics platform. Compare these two players based on their per-90 statistics:

**{p1['name']}** ({p1.get('team')}, {p1.get('position_group')}):
- Goals/90: {p1.get('goals_p90')} | xG/90: {p1.get('xg_p90')} | Assists/90: {p1.get('assists_p90')}
- Prog Passes/90: {p1.get('prog_passes_p90')} | Key Passes/90: {p1.get('key_passes_p90')}
- Pressures/90: {p1.get('pressures_p90')} | Tackles/90: {p1.get('tackles_p90')}
- Dribbles/90: {p1.get('dribbles_p90')} | Pass Completion: {p1.get('pass_completion')}%

**{p2['name']}** ({p2.get('team')}, {p2.get('position_group')}):
- Goals/90: {p2.get('goals_p90')} | xG/90: {p2.get('xg_p90')} | Assists/90: {p2.get('assists_p90')}
- Prog Passes/90: {p2.get('prog_passes_p90')} | Key Passes/90: {p2.get('key_passes_p90')}
- Pressures/90: {p2.get('pressures_p90')} | Tackles/90: {p2.get('tackles_p90')}
- Dribbles/90: {p2.get('dribbles_p90')} | Pass Completion: {p2.get('pass_completion')}%

Write a concise (150-200 word) analytical comparison. Highlight what each player does better, their key strengths, and in what team context each would thrive. Be specific with numbers."""

    response = CLIENT.messages.create(
        model=SONNET_MODEL,
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
    )
    ai_summary = response.content[0].text

    return {
        "player1": p1,
        "player2": p2,
        "stat_deltas": deltas,
        "ai_summary": ai_summary,
    }


# ---------------------------------------------------------------------------
# Player vs Team Fit
# ---------------------------------------------------------------------------

@router.post("/fit")
async def fit_analysis(req: FitAnalysisRequest):
    """
    Analyse how well a player fits a team's playing style.
    Returns fit score (0-100), category breakdown, valuation range, and AI explanation.
    """
    player = get_player_stats(req.player_id, season=req.season)
    team = get_team_profile(req.team_id, season=req.season)

    if not player:
        raise HTTPException(404, detail=f"Player not found: {req.player_id}")
    if not team:
        raise HTTPException(404, detail=f"Team not found: {req.team_id}")

    # Compute fit score
    fit = compute_fit_score(player, team)

    # Compute valuation
    valuation = estimate_value(player, fit_score=fit["overall_score"])

    # Generate AI explanation via Claude Sonnet
    ed = fit["explanation_data"]
    prompt = f"""You are FootIQ. Explain the fit between {ed['player_name']} and {ed['team_name']}.

Fit Score: {ed['overall_score']}/100
Category Scores: {ed['category_scores']}

Player Stats (per 90):
{ed['player_stats']}

Team Averages (per 90):
{ed['team_averages']}

Estimated transfer value for this team: \u20ac{valuation['min_value_m']}M - \u20ac{valuation['max_value_m']}M

Write 150-200 words explaining:
1. Why the score is what it is — what fits well, what doesn't
2. What the team would gain from signing this player
3. Any concerns or limitations
Be specific, cite the stats, be direct."""

    response = CLIENT.messages.create(
        model=SONNET_MODEL,
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
    )
    ai_explanation = response.content[0].text

    return {
        "player": player,
        "team": team,
        "fit_score": fit["overall_score"],
        "category_scores": fit["category_scores"],
        "dimension_scores": fit["dimension_scores"],
        "valuation": valuation,
        "ai_explanation": ai_explanation,
    }
