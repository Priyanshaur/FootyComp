-- FootIQ Database Schema
-- Run this in Supabase Dashboard > SQL Editor

-- Players table
CREATE TABLE IF NOT EXISTS players (
  id                      TEXT NOT NULL,
  season                  TEXT NOT NULL,
  name                    TEXT NOT NULL,
  team                    TEXT,
  league                  TEXT,
  position                TEXT,
  position_group          TEXT CHECK (position_group IN ('GK', 'DEF', 'MID', 'FWD')),
  age                     INTEGER,
  minutes                 INTEGER DEFAULT 0,
  -- Standard stats (per 90)
  goals_p90               FLOAT,
  assists_p90             FLOAT,
  xg_p90                  FLOAT,
  xag_p90                 FLOAT,
  npxg_p90                FLOAT,
  -- Passing (per 90)
  prog_passes_p90         FLOAT,
  key_passes_p90          FLOAT,
  pass_completion         FLOAT,
  -- Possession (per 90)
  prog_carries_p90        FLOAT,
  dribbles_p90            FLOAT,
  touches_att_third_p90   FLOAT,
  -- Defensive (per 90)
  tackles_p90             FLOAT,
  interceptions_p90       FLOAT,
  blocks_p90              FLOAT,
  -- Pressing (per 90)
  pressures_p90           FLOAT,
  press_success_pct       FLOAT,
  pressures_att_third_p90 FLOAT,
  -- Misc
  aerial_won_pct          FLOAT,
  updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (id, season)
);

-- Indexes for common search patterns
CREATE INDEX IF NOT EXISTS idx_players_name ON players USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);
CREATE INDEX IF NOT EXISTS idx_players_league ON players(league);
CREATE INDEX IF NOT EXISTS idx_players_position_group ON players(position_group);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
  id                          TEXT NOT NULL,
  season                      TEXT NOT NULL,
  name                        TEXT NOT NULL,
  league                      TEXT,
  -- Team-level style metrics (per 90)
  overall_pressures_p90       FLOAT,
  overall_pass_completion     FLOAT,
  overall_prog_passes_p90     FLOAT,
  overall_key_passes_p90      FLOAT,
  overall_tackles_p90         FLOAT,
  overall_interceptions_p90   FLOAT,
  overall_goals_p90           FLOAT,
  overall_xg_p90              FLOAT,
  overall_xga_p90             FLOAT,
  updated_at                  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (id, season)
);

CREATE INDEX IF NOT EXISTS idx_teams_name ON teams USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_teams_league ON teams(league);

-- Enable Row Level Security (RLS) - public read access
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read players" ON players FOR SELECT USING (true);
CREATE POLICY "Public read teams" ON teams FOR SELECT USING (true);

-- Service role can write (used by scraper)
CREATE POLICY "Service write players" ON players
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service write teams" ON teams
  FOR ALL USING (auth.role() = 'service_role');
