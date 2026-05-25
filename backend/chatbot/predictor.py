"""
Cup Competition AI Predictor (RAG Chatbot).

Fetches both teams' current stats from Supabase, injects them as context
into a Claude Haiku prompt, and streams the response token-by-token.
"""

import os
import logging
from typing import AsyncIterator
from dotenv import load_dotenv
import anthropic
from db.supabase_client import get_teams_by_ids

load_dotenv()
log = logging.getLogger(__name__)

CLIENT = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

HAIKU_MODEL = "claude-3-haiku-20240307"

SYSTEM_PROMPT = """You are FootIQ, a football analytics AI that predicts match outcomes based exclusively 
on real statistics provided to you. You must NEVER rely on historical reputation, club prestige, or 
facts from your training data.

Your analysis must:
1. Reference specific statistics from the data provided
2. Give a win probability estimate (e.g. "62% Bayern")
3. Give a predicted scoreline
4. Identify the 2-3 key matchup factors that drive your prediction
5. Be honest about uncertainty — football is unpredictable

Tone: Analytical but engaging. Like a top football analyst, not a robot.
Format: Use markdown with clear sections. Keep response under 400 words."""


def _build_team_context(team: dict) -> str:
    """Format a team's stats dict into a readable context string for Claude."""
    name = team.get("name", "Unknown")
    return f"""**{name}** (Season stats):
- Pressures per 90: {team.get('overall_pressures_p90', 'N/A')}
- Pass completion: {team.get('overall_pass_completion', 'N/A')}%
- Progressive passes per 90: {team.get('overall_prog_passes_p90', 'N/A')}
- Goals per 90: {team.get('overall_goals_p90', 'N/A')}
- xG per 90: {team.get('overall_xg_p90', 'N/A')}
- xGA per 90: {team.get('overall_xga_p90', 'N/A')}
- Tackles per 90: {team.get('overall_tackles_p90', 'N/A')}
- Interceptions per 90: {team.get('overall_interceptions_p90', 'N/A')}"""


def _build_rag_prompt(team1: dict, team2: dict, competition: str, user_message: str) -> str:
    """Build the user message with injected stats context."""
    context = f"""--- CURRENT SEASON STATISTICS (use ONLY these for your prediction) ---

{_build_team_context(team1)}

{_build_team_context(team2)}

--- COMPETITION: {competition} ---

USER QUESTION: {user_message}"""
    return context


async def stream_prediction(
    team1_id: str,
    team2_id: str,
    competition: str,
    user_message: str,
) -> AsyncIterator[str]:
    """
    Stream a match prediction from Claude Haiku with live stats as context.
    Yields text chunks as they arrive from the API.
    """
    # Fetch both teams from Supabase
    teams = get_teams_by_ids([team1_id, team2_id])
    team_map = {t["id"]: t for t in teams}

    team1 = team_map.get(team1_id)
    team2 = team_map.get(team2_id)

    if not team1 or not team2:
        missing = [tid for tid in [team1_id, team2_id] if tid not in team_map]
        yield f"Error: Could not find team data for: {', '.join(missing)}. Ensure teams have been scraped."
        return

    prompt = _build_rag_prompt(team1, team2, competition, user_message)
    log.info(f"Streaming prediction: {team1['name']} vs {team2['name']} [{competition}]")

    # Stream from Claude Haiku
    with CLIENT.messages.stream(
        model=HAIKU_MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def build_context_summary(team1_id: str, team2_id: str) -> dict:
    """Return the raw stats context used for the 'Show data used' panel in the frontend."""
    teams = get_teams_by_ids([team1_id, team2_id])
    return {t["id"]: t for t in teams}
