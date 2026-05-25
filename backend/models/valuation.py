"""
Transfer Valuation Model.

Estimates a player's market value range based on:
- Age
- Minutes / consistency
- Performance vs. position league average
- Fit score with the target team
"""

from typing import Optional
import math

# Base valuations (EUR millions) by position group — rough league medians
BASE_VALUE_M = {
    "FWD": 20.0,
    "MID": 15.0,
    "DEF": 12.0,
    "GK": 8.0,
}

# Peak age range where age factor = 1.0
PEAK_AGE_MIN = 23
PEAK_AGE_MAX = 27


def _age_factor(age: Optional[int]) -> float:
    """Return multiplier based on player age. Peak 23-27, decays outside."""
    if age is None:
        return 1.0
    if age < PEAK_AGE_MIN:
        # Rising — premium for youth
        return 1.0 + (PEAK_AGE_MIN - age) * 0.08
    elif age <= PEAK_AGE_MAX:
        return 1.0
    else:
        # Declining — discount per year after peak
        years_past_peak = age - PEAK_AGE_MAX
        return max(0.2, 1.0 - years_past_peak * 0.12)


def _minutes_factor(minutes: Optional[int]) -> float:
    """Return multiplier based on minutes played. Full season = ~2700-3200 mins."""
    if not minutes:
        return 0.5
    if minutes >= 2700:
        return 1.0
    if minutes >= 1800:
        return 0.85
    if minutes >= 900:
        return 0.70
    return 0.50


def _performance_factor(player: dict, position_group: str) -> float:
    """
    Estimate performance quality. Uses xG and xAG as proxy for attacking quality,
    tackles/pressures for defensive. Returns multiplier 0.5-1.8.
    """
    pos = position_group
    score = 1.0

    if pos == "FWD":
        xg = player.get("xg_p90") or 0
        # League average FWD xG/90 ~= 0.35
        ratio = xg / 0.35 if xg else 1.0
        score = 0.5 + min(ratio, 2.6) * 0.5

    elif pos == "MID":
        xag = player.get("xag_p90") or 0
        prog = player.get("prog_passes_p90") or 0
        ratio = (xag / 0.15 + prog / 5.0) / 2
        score = 0.5 + min(ratio, 2.6) * 0.5

    elif pos == "DEF":
        tackles = player.get("tackles_p90") or 0
        inter = player.get("interceptions_p90") or 0
        ratio = (tackles + inter) / 4.0  # ~4 combined is solid
        score = 0.5 + min(ratio, 2.6) * 0.5

    return round(max(0.5, min(2.0, score)), 3)


def _fit_factor(fit_score: float) -> float:
    """
    Premium a team might pay above market because of high fit.
    fit_score 0-100 -> multiplier 0.8-1.25
    """
    return round(0.8 + (fit_score / 100) * 0.45, 3)


def estimate_value(
    player: dict,
    fit_score: float,
    position_group: Optional[str] = None,
) -> dict:
    """
    Estimate transfer value range for a player.

    Returns:
        {
            min_value_m: float,   # EUR millions lower bound
            max_value_m: float,   # EUR millions upper bound
            central_value_m: float,
            factors: { age, minutes, performance, fit }
        }
    """
    pos = position_group or player.get("position_group", "MID")
    base = BASE_VALUE_M.get(pos, 15.0)

    af = _age_factor(player.get("age"))
    mf = _minutes_factor(player.get("minutes"))
    pf = _performance_factor(player, pos)
    ff = _fit_factor(fit_score)

    central = base * af * mf * pf
    # Fit factor adjusts what THIS team should pay (not absolute market value)
    team_specific = central * ff

    # +/-15% range
    spread = team_specific * 0.15
    return {
        "central_value_m": round(central, 1),
        "team_specific_value_m": round(team_specific, 1),
        "min_value_m": round(team_specific - spread, 1),
        "max_value_m": round(team_specific + spread, 1),
        "factors": {
            "age_factor": af,
            "minutes_factor": mf,
            "performance_factor": pf,
            "fit_factor": ff,
        },
    }
