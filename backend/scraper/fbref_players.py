"""
backend/scraper/fbref_players.py

Scrapes player statistics from FBref for all Big 5 European leagues
and stores them in Supabase. Uses the soccerdata library which wraps
FBref cleanly and handles rate limiting automatically.

Run from the backend/ directory:
    python -m scraper.fbref_players
"""

import time
import re
import pandas as pd
import soccerdata as sd  # type: ignore
from db.supabase_client import upsert_players_bulk

# ── Config ─────────────────────────────────────────────────────────────────────

SEASON = "2024-2025"

# soccerdata league codes → display names
LEAGUES = {
    "ENG-Premier League":   "Premier League",
    "ESP-La Liga":          "La Liga",
    "GER-Bundesliga":       "Bundesliga",
    "ITA-Serie A":          "Serie A",
    "FRA-Ligue 1":          "Ligue 1",
}

# Minimum minutes to include a player (filters out players with 1 appearance)
MIN_MINUTES = 90


# ── Helpers ────────────────────────────────────────────────────────────────────

def safe_float(val) -> float | None:
    """Convert a value to float, returning None if not possible."""
    try:
        f = float(val)
        return None if pd.isna(f) else round(f, 3)
    except (TypeError, ValueError):
        return None


def safe_int(val) -> int | None:
    """Convert a value to int, returning None if not possible."""
    try:
        f = float(val)
        return None if pd.isna(f) else int(f)
    except (TypeError, ValueError):
        return None


def make_player_id(name: str, team: str, season: str) -> str:
    """
    Generate a stable unique ID for a player.
    e.g. "Lionel Messi" + "Inter Miami" + "2024-2025" → "lionelmessi_intermiami_2425"
    """
    def clean(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())
    season_short = season.replace("20", "").replace("-", "")
    return f"{clean(name)}_{clean(team)}_{season_short}"


def per90(value, minutes: int) -> float | None:
    """Normalize a raw count stat to per-90-minutes."""
    if value is None or minutes is None or minutes < 1:
        return None
    try:
        return round((float(value) / minutes) * 90, 3)
    except (TypeError, ValueError):
        return None


def normalize_position(raw_pos: str) -> str:
    """
    Normalize FBref position strings to simple categories.
    FBref uses formats like "FW,MF" — we take the primary position.
    """
    if not raw_pos or pd.isna(raw_pos):
        return "Unknown"
    primary = str(raw_pos).split(",")[0].strip().upper()
    if primary in ("FW", "CF", "LW", "RW"):
        return "FW"
    if primary in ("MF", "CM", "AM", "DM", "LM", "RM"):
        return "MF"
    if primary in ("DF", "CB", "LB", "RB", "LWB", "RWB"):
        return "DF"
    if primary == "GK":
        return "GK"
    return primary


# ── Stat Fetchers ──────────────────────────────────────────────────────────────

def fetch_standard_stats(fbref: sd.FBref) -> pd.DataFrame:
    """Goals, assists, xG, xAG, minutes, age, position."""
    print("  Fetching standard stats...")
    df = fbref.read_player_season_stats(stat_type="standard")
    df = df.reset_index()
    return df


def fetch_passing_stats(fbref: sd.FBref) -> pd.DataFrame:
    """Pass completion, progressive passes, key passes, short/medium/long split."""
    print("  Fetching passing stats...")
    df = fbref.read_player_season_stats(stat_type="passing")
    df = df.reset_index()
    return df


def fetch_possession_stats(fbref: sd.FBref) -> pd.DataFrame:
    """Touches, progressive carries, dribbles."""
    print("  Fetching possession stats...")
    df = fbref.read_player_season_stats(stat_type="possession")
    df = df.reset_index()
    return df


def fetch_defensive_stats(fbref: sd.FBref) -> pd.DataFrame:
    """Tackles, interceptions, blocks, clearances, aerials."""
    print("  Fetching defensive stats...")
    df = fbref.read_player_season_stats(stat_type="defense")
    df = df.reset_index()
    return df


def fetch_pressing_stats(fbref: sd.FBref) -> pd.DataFrame:
    """Pressures, press success rate, pressures by third."""
    print("  Fetching pressing stats...")
    df = fbref.read_player_season_stats(stat_type="misc")
    df = df.reset_index()
    return df


# ── Column Finder ──────────────────────────────────────────────────────────────

def find_col(df: pd.DataFrame, *candidates) -> str | None:
    """
    Find the first matching column name from a list of candidates.
    FBref column names can vary slightly between scrapes so we check
    multiple possible names for the same stat.
    """
    cols_lower = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in cols_lower:
            return cols_lower[candidate.lower()]
    return None


# ── Main Builder ───────────────────────────────────────────────────────────────

def build_player_rows(league_code: str, league_name: str) -> list[dict]:
    """
    Fetch all stat tables for one league, merge them, and return
    a list of player dicts ready for Supabase upsert.
    """
    print(f"\nProcessing {league_name}...")

    fbref = sd.FBref(leagues=league_code, seasons=SEASON)

    # Fetch all stat categories
    std   = fetch_standard_stats(fbref)
    pas   = fetch_passing_stats(fbref)
    pos   = fetch_possession_stats(fbref)
    defn  = fetch_defensive_stats(fbref)
    misc  = fetch_pressing_stats(fbref)

    # soccerdata returns a MultiIndex — flatten it
    for df in [std, pas, pos, defn, misc]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join([str(c) for c in col if str(c) != '']).strip('_')
                          for col in df.columns]

    # We build from standard stats as the base
    # and merge the others in by player name + team
    merge_keys = ["player", "team"] if "player" in std.columns else ["Player", "Squad"]

    def safe_merge(base, other):
        shared = [c for c in merge_keys if c in base.columns and c in other.columns]
        if not shared:
            return base
        # Drop duplicate columns except merge keys
        other_cols = shared + [c for c in other.columns if c not in base.columns]
        return base.merge(other[other_cols], on=shared, how="left")

    merged = std.copy()
    for df in [pas, pos, defn, misc]:
        merged = safe_merge(merged, df)

    print(f"  Merged dataframe: {len(merged)} rows, {len(merged.columns)} columns")

    # Filter minimum minutes
    min_col = find_col(merged, "minutes_90s", "Min", "min", "minutes")
    if min_col:
        merged[min_col] = pd.to_numeric(merged[min_col], errors="coerce")
        # soccerdata sometimes stores minutes as 90s (i.e. 30.5 = 2745 minutes)
        if merged[min_col].median() < 100:
            # It's in 90s format — convert to actual minutes
            merged["_minutes"] = merged[min_col] * 90
        else:
            merged["_minutes"] = merged[min_col]
        merged = merged[merged["_minutes"] >= MIN_MINUTES]
    else:
        merged["_minutes"] = 900  # fallback

    print(f"  After filtering <{MIN_MINUTES} mins: {len(merged)} players")

    players = []

    for _, row in merged.iterrows():

        # ── Identity ────────────────────────────────────────────────────────
        name_col   = find_col(merged, "player", "Player", "name")
        team_col   = find_col(merged, "team", "Team", "Squad", "squad")
        pos_col    = find_col(merged, "position", "Pos", "pos")
        age_col    = find_col(merged, "age", "Age")
        nation_col = find_col(merged, "nationality", "Nation", "nation")

        name  = str(row[name_col]) if name_col else "Unknown"
        team  = str(row[team_col]) if team_col else "Unknown"
        minutes = float(row.get("_minutes", 900) or 900)

        # ── Standard Stats ───────────────────────────────────────────────────
        goals_col   = find_col(merged, "goals", "Gls", "gls")
        assists_col = find_col(merged, "assists", "Ast", "ast")
        xg_col      = find_col(merged, "xg", "xG", "expected_xg")
        xag_col     = find_col(merged, "xag", "xAG", "expected_xag")
        shots_col   = find_col(merged, "shots", "Sh", "sh")
        sot_col     = find_col(merged, "shots_on_target", "SoT", "sot")

        # ── Passing ──────────────────────────────────────────────────────────
        pass_cmp_col  = find_col(merged, "passes_completed", "Cmp", "total_cmp")
        pass_pct_col  = find_col(merged, "passes_pct", "Cmp%", "total_cmp_pct")
        prog_pass_col = find_col(merged, "progressive_passes", "PrgP", "prgp")
        key_pass_col  = find_col(merged, "assisted_shots", "KP", "kp")
        short_pct_col = find_col(merged, "passes_short_pct", "short_cmp_pct", "Cmp%_short")
        med_pct_col   = find_col(merged, "passes_medium_pct", "medium_cmp_pct", "Cmp%_medium")
        long_pct_col  = find_col(merged, "passes_long_pct", "long_cmp_pct", "Cmp%_long")

        # ── Possession ───────────────────────────────────────────────────────
        touches_col      = find_col(merged, "touches", "Touches", "touches_touches")
        touches_att_col  = find_col(merged, "touches_att_3rd", "Att 3rd", "touches_att_3rd")
        prog_carries_col = find_col(merged, "progressive_carries", "PrgC", "carries_prgc")
        drib_col         = find_col(merged, "dribbles_completed", "Succ", "take_ons_succ")
        drib_pct_col     = find_col(merged, "dribbles_completed_pct", "Succ%", "take_ons_succ_pct")

        # ── Defensive ────────────────────────────────────────────────────────
        tackles_col     = find_col(merged, "tackles", "Tkl", "tackles_tkl")
        tackle_pct_col  = find_col(merged, "tackles_won_pct", "Tkl%", "challenges_tkl_pct")
        interceptions_col = find_col(merged, "interceptions", "Int", "int")
        blocks_col      = find_col(merged, "blocks", "Blocks", "blocks_blocks")
        clearances_col  = find_col(merged, "clearances", "Clr", "clr")
        aerials_col     = find_col(merged, "aerials_won_pct", "Won%", "aerial_duels_won_pct")

        # ── Pressing ─────────────────────────────────────────────────────────
        press_col        = find_col(merged, "pressures", "Press", "press")
        press_succ_col   = find_col(merged, "pressure_success_pct", "Succ%_press", "%_press")
        press_att_col    = find_col(merged, "pressures_att_3rd", "Att 3rd_press")
        press_mid_col    = find_col(merged, "pressures_mid_3rd", "Mid 3rd_press")
        press_def_col    = find_col(merged, "pressures_def_3rd", "Def 3rd_press")

        # ── Playing Time ─────────────────────────────────────────────────────
        matches_col = find_col(merged, "games", "MP", "mp")
        starts_col  = find_col(merged, "games_starts", "Starts", "starts")

        player_row = {
            "id":         make_player_id(name, team, SEASON),
            "name":       name,
            "team":       team,
            "league":     league_name,
            "season":     SEASON,
            "position":   normalize_position(row[pos_col] if pos_col else None),
            "age":        safe_int(row[age_col]) if age_col else None,
            "nationality": str(row[nation_col]) if nation_col and not pd.isna(row.get(nation_col, float('nan'))) else None,

            # Standard (per 90)
            "goals_p90":            per90(row.get(goals_col),   minutes),
            "assists_p90":          per90(row.get(assists_col), minutes),
            "xg_p90":               per90(row.get(xg_col),      minutes),
            "xag_p90":              per90(row.get(xag_col),     minutes),
            "shots_p90":            per90(row.get(shots_col),   minutes),
            "shots_on_target_p90":  per90(row.get(sot_col),     minutes),

            # Passing (per 90 where appropriate)
            "passes_completed_p90":     per90(row.get(pass_cmp_col),  minutes),
            "pass_completion_pct":      safe_float(row.get(pass_pct_col)),
            "progressive_passes_p90":   per90(row.get(prog_pass_col), minutes),
            "key_passes_p90":           per90(row.get(key_pass_col),  minutes),
            "passes_short_pct":         safe_float(row.get(short_pct_col)),
            "passes_medium_pct":        safe_float(row.get(med_pct_col)),
            "passes_long_pct":          safe_float(row.get(long_pct_col)),

            # Possession (per 90)
            "touches_p90":              per90(row.get(touches_col),      minutes),
            "touches_att_third_p90":    per90(row.get(touches_att_col),  minutes),
            "progressive_carries_p90":  per90(row.get(prog_carries_col), minutes),
            "dribbles_completed_p90":   per90(row.get(drib_col),         minutes),
            "dribble_success_pct":      safe_float(row.get(drib_pct_col)),

            # Defensive (per 90)
            "tackles_p90":          per90(row.get(tackles_col),      minutes),
            "tackle_success_pct":   safe_float(row.get(tackle_pct_col)),
            "interceptions_p90":    per90(row.get(interceptions_col), minutes),
            "blocks_p90":           per90(row.get(blocks_col),        minutes),
            "clearances_p90":       per90(row.get(clearances_col),    minutes),
            "aerials_won_pct":      safe_float(row.get(aerials_col)),

            # Pressing (per 90)
            "pressures_p90":            per90(row.get(press_col),      minutes),
            "pressure_success_pct":     safe_float(row.get(press_succ_col)),
            "pressures_att_third_p90":  per90(row.get(press_att_col),  minutes),
            "pressures_mid_third_p90":  per90(row.get(press_mid_col),  minutes),
            "pressures_def_third_p90":  per90(row.get(press_def_col),  minutes),

            # Playing time
            "matches_played":   safe_int(row.get(matches_col)),
            "starts":           safe_int(row.get(starts_col)),
            "minutes_played":   safe_int(minutes),
        }

        players.append(player_row)

    return players


# ── Entry Point ────────────────────────────────────────────────────────────────

def run():
    """Scrape all leagues and push to Supabase."""
    print("=" * 60)
    print("FootIQ Player Scraper")
    print(f"Season: {SEASON}")
    print(f"Leagues: {', '.join(LEAGUES.values())}")
    print("=" * 60)

    total = 0

    for league_code, league_name in LEAGUES.items():
        try:
            players = build_player_rows(league_code, league_name)
            if players:
                upsert_players_bulk(players)
                total += len(players)
                print(f"  ✓ {league_name}: {len(players)} players saved")
            else:
                print(f"  ✗ {league_name}: no players returned")

            # Be polite to FBref — wait between leagues
            time.sleep(5)

        except Exception as e:
            print(f"  ✗ {league_name} failed: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"Done. Total players saved: {total}")
    print("=" * 60)


if __name__ == "__main__":
    run()