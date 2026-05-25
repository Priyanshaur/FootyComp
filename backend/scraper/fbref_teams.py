"""
Scrapes team-level statistics from FBref for all Big 5 European leagues.
Builds a 'style profile' per team per position group, used for the fit model.

Run standalone: python -m scraper.fbref_teams
"""

import logging
from typing import Optional
import pandas as pd
import soccerdata as sd
from db.supabase_client import upsert_teams

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BIG5_LEAGUES = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
SEASONS = ["2324", "2425"]


def scrape_team_season(season: str) -> list[dict]:
    """Scrape team-level stats for a season and return list of team profile dicts."""
    log.info(f"Scraping team stats for season {season}")
    fbref = sd.FBref(leagues=BIG5_LEAGUES, seasons=season)

    stat_types = ["standard", "passing", "possession", "defense"]
    dfs = []
    for table in stat_types:
        try:
            log.info(f"  Fetching team table: {table}")
            raw = fbref.read_team_season_stats(stat_type=table)
            raw = raw.reset_index()
            dfs.append(raw)
        except Exception as e:
            log.warning(f"  Failed to fetch team {table}: {e}")

    if not dfs:
        raise RuntimeError(f"No team tables fetched for season {season}")

    combined = dfs[0]
    for df in dfs[1:]:
        merge_keys = ["team", "league", "season"]
        merge_keys = [c for c in merge_keys if c in combined.columns and c in df.columns]
        new_cols = [c for c in df.columns if c not in combined.columns or c in merge_keys]
        combined = combined.merge(df[new_cols], on=merge_keys, how="left")

    records = []
    for _, row in combined.iterrows():
        team_name = str(row.get("team", ""))
        league = str(row.get("league", ""))
        team_id = f"{team_name.lower().replace(' ', '_')}_{league.lower().replace(' ', '_').replace('-', '_')}"
        minutes = float(row.get("minutes", 1) or 1)

        def p90(col):
            val = row.get(col)
            if val is None or pd.isna(val):
                return None
            return round(float(val) / minutes * 90, 4)

        rec = {
            "id": team_id,
            "name": team_name,
            "league": league,
            "season": season,
            # Team-level aggregated style metrics
            "overall_pressures_p90": p90("pressures"),
            "overall_pass_completion": float(row.get("passes_pct", 0) or 0),
            "overall_prog_passes_p90": p90("progressive_passes"),
            "overall_key_passes_p90": p90("key_passes"),
            "overall_tackles_p90": p90("tackles"),
            "overall_interceptions_p90": p90("interceptions"),
            "overall_goals_p90": p90("goals"),
            "overall_xg_p90": p90("xg"),
            "overall_xga_p90": p90("xga"),
        }
        records.append(rec)

    return records


def run_scrape(seasons: Optional[list[str]] = None, push_to_db: bool = True):
    """Main entry point: scrape team stats for all seasons."""
    if seasons is None:
        seasons = SEASONS

    all_records = []
    for season in seasons:
        records = scrape_team_season(season)
        all_records.extend(records)
        log.info(f"  Built {len(records)} team records for {season}")
        if push_to_db:
            upsert_teams(records)
            log.info(f"  Pushed {len(records)} team records to Supabase")

    return all_records


if __name__ == "__main__":
    run_scrape()
