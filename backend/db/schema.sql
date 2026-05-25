-- ============================================================
-- FootIQ Database Schema
-- Run this in Supabase Dashboard → SQL Editor
-- ============================================================


-- ============================================================
-- 1. PLAYERS TABLE
-- One row per player per season
-- ============================================================
CREATE TABLE IF NOT EXISTS players (
    id                  TEXT PRIMARY KEY,           -- e.g. "messilionel_2425"
    name                TEXT NOT NULL,
    team                TEXT NOT NULL,
    league              TEXT NOT NULL,              -- "Premier League", "La Liga", etc.
    season              TEXT NOT NULL,              -- "2024-2025"
    nationality         TEXT,
    position            TEXT,                       -- "FW", "MF", "DF", "GK"
    age                 INTEGER,

    -- Standard Stats (per 90)
    goals_p90           FLOAT,
    assists_p90         FLOAT,
    xg_p90              FLOAT,
    xag_p90             FLOAT,
    shots_p90           FLOAT,
    shots_on_target_p90 FLOAT,

    -- Passing (per 90)
    passes_completed_p90        FLOAT,
    pass_completion_pct         FLOAT,
    progressive_passes_p90      FLOAT,
    key_passes_p90              FLOAT,
    passes_short_pct            FLOAT,
    passes_medium_pct           FLOAT,
    passes_long_pct             FLOAT,

    -- Possession (per 90)
    touches_p90                 FLOAT,
    touches_att_third_p90       FLOAT,
    progressive_carries_p90     FLOAT,
    dribbles_completed_p90      FLOAT,
    dribble_success_pct         FLOAT,

    -- Defensive Actions (per 90)
    tackles_p90                 FLOAT,
    tackle_success_pct          FLOAT,
    interceptions_p90           FLOAT,
    blocks_p90                  FLOAT,
    clearances_p90              FLOAT,
    aerials_won_pct             FLOAT,

    -- Pressing (per 90)
    pressures_p90               FLOAT,
    pressure_success_pct        FLOAT,
    pressures_att_third_p90     FLOAT,
    pressures_mid_third_p90     FLOAT,
    pressures_def_third_p90     FLOAT,

    -- Playing Time
    matches_played      INTEGER,
    starts              INTEGER,
    minutes_played      INTEGER,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 2. TEAMS TABLE
-- One row per team per season
-- Stores the team's AVERAGE stats by position group
-- This is the "team style profile" used for fit analysis
-- ============================================================
CREATE TABLE IF NOT EXISTS teams (
    id                  TEXT PRIMARY KEY,           -- e.g. "manchester_city_2425"
    name                TEXT NOT NULL,
    league              TEXT NOT NULL,
    season              TEXT NOT NULL,

    -- Team-level pressing profile
    pressures_p90               FLOAT,
    pressure_success_pct        FLOAT,
    pressures_att_third_p90     FLOAT,

    -- Team-level passing profile
    pass_completion_pct         FLOAT,
    progressive_passes_p90      FLOAT,
    passes_long_pct             FLOAT,

    -- Team-level possession profile
    progressive_carries_p90     FLOAT,
    dribbles_completed_p90      FLOAT,

    -- Team-level defensive profile
    tackles_p90                 FLOAT,
    interceptions_p90           FLOAT,
    blocks_p90                  FLOAT,
    aerials_won_pct             FLOAT,

    -- Team-level attacking profile
    goals_p90                   FLOAT,
    xg_p90                      FLOAT,
    shots_p90                   FLOAT,

    -- Positional averages for fit scoring
    -- Forward profile
    fw_pressures_p90            FLOAT,
    fw_goals_p90                FLOAT,
    fw_xg_p90                   FLOAT,
    fw_progressive_carries_p90  FLOAT,
    fw_dribbles_p90             FLOAT,

    -- Midfielder profile
    mf_pressures_p90            FLOAT,
    mf_progressive_passes_p90   FLOAT,
    mf_key_passes_p90           FLOAT,
    mf_tackles_p90              FLOAT,
    mf_progressive_carries_p90  FLOAT,

    -- Defender profile
    df_pressures_p90            FLOAT,
    df_tackles_p90              FLOAT,
    df_interceptions_p90        FLOAT,
    df_aerials_won_pct          FLOAT,
    df_passes_long_pct          FLOAT,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 3. FIT SCORES TABLE
-- Cached results of player-team fit analyses
-- So we don't recompute every time someone requests the same pair
-- ============================================================
CREATE TABLE IF NOT EXISTS fit_scores (
    id                  SERIAL PRIMARY KEY,
    player_id           TEXT REFERENCES players(id),
    team_id             TEXT REFERENCES teams(id),
    season              TEXT NOT NULL,

    -- Overall score
    fit_score           FLOAT NOT NULL,             -- 0 to 100

    -- Category breakdown
    pressing_score      FLOAT,
    passing_score       FLOAT,
    defensive_score     FLOAT,
    attacking_score     FLOAT,
    possession_score    FLOAT,

    -- Transfer valuation
    estimated_value_low_eur     BIGINT,             -- e.g. 20000000
    estimated_value_high_eur    BIGINT,             -- e.g. 35000000

    -- AI explanation (cached so we don't re-call Claude every time)
    ai_explanation      TEXT,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(player_id, team_id, season)
);


-- ============================================================
-- 4. MATCH PREDICTIONS TABLE
-- Cached cup competition predictions from the chatbot
-- ============================================================
CREATE TABLE IF NOT EXISTS match_predictions (
    id                  SERIAL PRIMARY KEY,
    home_team           TEXT NOT NULL,
    away_team           TEXT NOT NULL,
    competition         TEXT NOT NULL,              -- "Champions League", "FA Cup", etc.
    round               TEXT,                       -- "Round of 16", "Quarter Final", etc.

    -- Prediction output
    predicted_winner    TEXT,
    home_win_prob       FLOAT,                      -- 0 to 1
    draw_prob           FLOAT,
    away_win_prob       FLOAT,
    predicted_score     TEXT,                       -- e.g. "2-1"

    -- Full AI response cached
    ai_response         TEXT,

    -- Stats snapshot used for this prediction (for transparency)
    home_stats_snapshot JSONB,
    away_stats_snapshot JSONB,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 5. INDEXES
-- Speed up the most common queries
-- ============================================================

-- Search players by name (used in the search bar)
CREATE INDEX IF NOT EXISTS idx_players_name
    ON players USING GIN (to_tsvector('english', name));

-- Filter players by league and season
CREATE INDEX IF NOT EXISTS idx_players_league_season
    ON players(league, season);

-- Filter players by team
CREATE INDEX IF NOT EXISTS idx_players_team
    ON players(team);

-- Filter players by position (for fit scoring)
CREATE INDEX IF NOT EXISTS idx_players_position
    ON players(position);

-- Search teams by name
CREATE INDEX IF NOT EXISTS idx_teams_name
    ON teams USING GIN (to_tsvector('english', name));

-- Filter teams by league
CREATE INDEX IF NOT EXISTS idx_teams_league
    ON teams(league, season);

-- Look up cached fit scores quickly
CREATE INDEX IF NOT EXISTS idx_fit_scores_lookup
    ON fit_scores(player_id, team_id, season);


-- ============================================================
-- 6. AUTO-UPDATE updated_at TRIGGER
-- Automatically updates the updated_at column on any row change
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER players_updated_at
    BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================
-- 7. ROW LEVEL SECURITY
-- Allow public read access (needed for the frontend)
-- Restrict writes to service role only (your backend)
-- ============================================================
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE fit_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_predictions ENABLE ROW LEVEL SECURITY;

-- Anyone can read
CREATE POLICY "Public read players"
    ON players FOR SELECT USING (true);

CREATE POLICY "Public read teams"
    ON teams FOR SELECT USING (true);

CREATE POLICY "Public read fit_scores"
    ON fit_scores FOR SELECT USING (true);

CREATE POLICY "Public read match_predictions"
    ON match_predictions FOR SELECT USING (true);

-- Only the backend (service role) can write
CREATE POLICY "Service role write players"
    ON players FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write teams"
    ON teams FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write fit_scores"
    ON fit_scores FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write match_predictions"
    ON match_predictions FOR ALL USING (auth.role() = 'service_role');