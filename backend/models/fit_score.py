"""
Player-Team Fit Scoring Model.

Compares a player's per-90 stats against a team's style profile.
Outputs a Fit Score (0-100) with a category breakdown.
"""

from typing import Optional
import math

# Position-specific weights for each stat dimension
# Keys must match column names in Supabase players table
POSITION_WEIGHTS = {
    "FWD": {
        "goals_p90": 0.20,
        "xg_p90": 0.18,
        "npxg_p90": 0.12,
        "pressures_p90": 0.12,
        "dribbles_p90": 0.12,
        "prog_carries_p90": 0.14,
        "key_passes_p90": 0.12,
    },
    "MID": {
        "prog_passes_p90": 0.20,
        "key_passes_p90": 0.18,
        "pressures_p90": 0.18,
        "tackles_p90": 0.14,
        "dribbles_p90": 0.14,
        "xag_p90": 0.16,
    },
    "DEF": {
        "tackles_p90": 0.25,
        "interceptions_p90": 0.25,
        "aerial_won_pct": 0.20,
        "pressures_p90": 0.15,
        "pass_completion": 0.15,
    },
    "GK": {
        "pass_completion": 0.50,
        "aerial_won_pct": 0.50,
    },
}

# Mapping from team profile columns to player columns (for comparison)
# team_col -> player_col
TEAM_TO_PLAYER_MAP = {
    "overall_pressures_p90": "pressures_p90",
    "overall_pass_completion": "pass_completion",
    "overall_prog_passes_p90": "prog_passes_p90",
    "overall_key_passes_p90": "key_passes_p90",
    "overall_tackles_p90": "tackles_p90",
    "overall_interceptions_p90": "interceptions_p90",
    "overall_goals_p90": "goals_p90",
    "overall_xg_p90": "xg_p90",
}

# Category groupings for the breakdown display
CATEGORIES = {
    "Attacking": ["goals_p90", "xg_p90", "npxg_p90", "key_passes_p90", "xag_p90"],
    "Possession": ["prog_passes_p90", "prog_carries_p90", "dribbles_p90", "pass_completion"],
    "Pressing": ["pressures_p90", "pressures_att_third_p90"],
    "Defensive": ["tackles_p90", "interceptions_p90", "blocks_p90", "aerial_won_pct"],
}


def _sigmoid_score(diff_pct: float) -> float:
    """
    Map a percentage difference to a 0-100 score using a sigmoid.
    diff_pct = (player_val - team_avg) / team_avg
    0% diff -> 50 score
    +50% above team avg -> ~80 score
    -50% below team avg -> ~20 score
    """
    return round(100 / (1 + math.exp(-3 * diff_pct)), 2)


def compute_fit_score(
    player: dict,
    team: dict,
    position_group: Optional[str] = None,
) -> dict:
    """
    Compute fit score for a player against a team.

    Args:
        player: Player stats dict from Supabase
        team: Team profile dict from Supabase
        position_group: Override position group (FWD/MID/DEF/GK)

    Returns:
        {
            overall_score: int (0-100),
            category_scores: {"Attacking": 72, "Possession": 85, ...},
            dimension_scores: {"goals_p90": 68, ...},
            explanation_data: {...}  # raw data for Claude prompt
        }
    """
    pos = position_group or player.get("position_group", "MID")
    weights = POSITION_WEIGHTS.get(pos, POSITION_WEIGHTS["MID"])

    # Build team averages in player-column space
    team_avgs = {}
    for team_col, player_col in TEAM_TO_PLAYER_MAP.items():
        val = team.get(team_col)
        if val is not None:
            team_avgs[player_col] = float(val)

    dimension_scores = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for stat, weight in weights.items():
        player_val = player.get(stat)
        team_avg = team_avgs.get(stat)

        if player_val is None or team_avg is None or team_avg == 0:
            # Can't compute this dimension — skip it and redistribute weight
            continue

        diff_pct = (float(player_val) - float(team_avg)) / float(team_avg)
        score = _sigmoid_score(diff_pct)
        dimension_scores[stat] = score
        weighted_sum += score * weight
        total_weight += weight

    overall = round(weighted_sum / total_weight, 1) if total_weight > 0 else 50.0

    # Category breakdowns
    category_scores = {}
    for cat_name, cat_stats in CATEGORIES.items():
        relevant = [dimension_scores[s] for s in cat_stats if s in dimension_scores]
        if relevant:
            category_scores[cat_name] = round(sum(relevant) / len(relevant), 1)

    explanation_data = {
        "player_name": player.get("name"),
        "team_name": team.get("name"),
        "position_group": pos,
        "overall_score": overall,
        "category_scores": category_scores,
        "key_dimensions": dimension_scores,
        "player_stats": {k: player.get(k) for k in weights.keys()},
        "team_averages": {k: team_avgs.get(k) for k in weights.keys()},
    }

    return {
        "overall_score": overall,
        "category_scores": category_scores,
        "dimension_scores": dimension_scores,
        "explanation_data": explanation_data,
    }
