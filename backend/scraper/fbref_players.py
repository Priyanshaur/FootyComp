"""
Scrapes player statistics from FBref for all Big 5 European leagues.
Uses the `soccerdata` library which wraps FBref cleanly.

Run standalone: python -m scraper.fbref_players
"""

import logging
from typing import Optional
import pandas as pd
import soccerdata as sd
from db.supabase_client import upsert_players

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BIG5_LEAGUES = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
SEASONS = ["2324", "2425"]  # 2023-24 and 2024-25

# Stats tables to fetch from FBref via soccerdata
STAT_TABLES = [
    "standard",
    "passing",
    "passing_types",
    "possession",
    "defense",
    "misc",
    "playing_time",
]

# Columns to keep per table (maps soccerdata column names to our schema)
COLUMN_MAP = {
    # standard stats
    "goals": "goals_p90",
    "assists": "assists_p90",
    "xg": "xg_p90",
    "xag": "xag_p90",
    "npxg": "npxg_p90",
    # passing
    "progressive_passes": "prog_passes_p90",
    "key_passes": "key_passes_p90",
    "passes_pct": "pass_completion",
    # possession
    "progressive_carries": "prog_carries_p90",
    "dribbles_completed": "dribbles_p90",
    "touches_att_3rd": "touches_att_third_p90",
    # defense
    "tackles": "tackles_p90",
    "interceptions": "interceptions_p90",
    "blocks": "blocks_p90",
    # misc
    "aerials_won_pct": "aerial_won_pct",
    # pressing (from standard/misc)
    "pressures": "pressures_p90",
    "pressure_regains": "press_success_pct",
    "pressures_att_3rd": "pressures_att_third_p90",
}

# Rate stats to normalise to per 90 (cols that are totals, not already per 90)
RATE_COLS = [
    "goals_p90", "assists_p90", "xg_p90", "xag_p90", "npxg_p90",
    "prog_passes_p90", "key_passes_p90",
    "prog_carries_p90", "dribbles_p90", "touches_att_third_p90",
    "tackles_p90", "interceptions_p90", "blocks_p90",
    "pressures_p90", "pressures_att_third_p90",
]

POSITION_MAP = {
    "GK": "GK",
    "DF": "DEF", "CB": "DEF", "LB": "DEF", "RB": "DEF", "WB": "DEF",
    "MF": "MID", "CM": "MID", "DM": "MID", "AM": "MID",
    "FW": "FWD", "LW": "FWD", "RW": "FWD", "CF": "FWD",
}


def _map_position_group(pos: str) -> str:
    """Map FBref position string to our 4-group system."""
    if not pos or pd.isna(pos):
        return "MID"
    primary = str(pos).split(",")[0].strip().upper()
    return POSITION_MAP.get(primary, "MID")


def _normalise_per90(df: pd.DataFrame, minutes_col: str = "minutes") -> pd.DataFrame:
    """Normalise rate columns to per-90-minutes values."""
    if minutes_col not in df.columns:
        return df
    minutes = df[minutes_col].replace(0, pd.NA)
    for col in RATE_COLS:
        if col in df.columns:
            df[col] = (df[col] / minutes * 90).round(4)
    return df


def scrape_season(season: str) -> pd.DataFrame:
    """
    Scrape all player stats for a given season across all Big 5 leagues.
    Returns a combined DataFrame normalised to per-90 values.
    """
    log.info(f"Starting scrape for season {season}")
    fbref = sd.FBref(leagues=BIG5_LEAGUES, seasons=season)

    dfs = []
    for table in STAT_TABLES:
        try:
            log.info(f"  Fetching table: {table}")
            raw = fbref.read_player_season_stats(stat_type=table)
            raw = raw.reset_index()
            dfs.append(raw)
        except Exception as e:
            log.warning(f"  Failed to fetch {table}: {e}")

    if not dfs:
        raise RuntimeError(f"No tables fetched for season {season}")

    # Merge all tables on player+team+season
    combined = dfs[0]
    for df in dfs[1:]:
        shared_cols = ["player", "team", "league", "season", "pos", "age", "minutes"]
        merge_keys = [c for c in shared_cols if c in combined.columns and c in df.columns]
        # Drop columns that already exist to avoid duplicates
        new_cols = [c for c in df.columns if c not in combined.columns or c in merge_keys]
        combined = combined.merge(df[new_cols], on=merge_keys, how="left")

    return combined


def _build_records(df: pd.DataFrame, season: str) -> list[dict]:
    """Transform raw DataFrame into list of dicts matching our Supabase schema."""
    records = []
    for _, row in df.iterrows():
        # Build stable player ID from name + team
        player_id = f"{str(row.get('player', '')).lower().replace(' ', '_')}_{str(row.get('team', '')).lower().replace(' ', '_')}"
        rec = {
            "id": player_id,
            "name": row.get("player", ""),
            "team": row.get("team", ""),
            "league": row.get("league", ""),
            "position": row.get("pos", ""),
            "position_group": _map_position_group(row.get("pos", "")),
            "season": season,
            "age": int(row.get("age", 0)) if pd.notna(row.get("age")) else None,
            "minutes": int(row.get("minutes", 0)) if pd.notna(row.get("minutes")) else 0,
        }
        # Map stat columns
        for src, dst in COLUMN_MAP.items():
            val = row.get(src)
            rec[dst] = float(val) if pd.notna(val) else None
        records.append(rec)
    return records


def run_scrape(seasons: Optional[list[str]] = None, push_to_db: bool = True):
    """Main entry point: scrape all seasons and optionally push to Supabase."""
    if seasons is None:
        seasons = SEASONS

    for season in seasons:
        log.info(f"Processing season {season}")
        df = scrape_season(season)
        df = _normalise_per90(df)
        records = _build_records(df, season)
        log.info(f"  Built {len(records)} player records for {season}")
        if push_to_db:
            upsert_players(records)
            log.info(f"  Pushed {len(records)} records to Supabase")
        else:
            log.info("  push_to_db=False, skipping Supabase write")

    return records  # returns last season's records for inspection


if __name__ == "__main__":
    run_scrape()
