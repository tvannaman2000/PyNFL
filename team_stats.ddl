# ========================================
# database/team_stats.sql
# Version: 1.0
# ========================================

"""
Team Statistics Table

Stores comprehensive team statistics for each game, including quarter-by-quarter
scoring and all major statistical categories. Each team gets one record per game
with their offensive stats, allowing defensive stats to be queried by looking
at what opponents did against them.

Example: Cards score 13 points in Q1 vs Packers
- Cards offensive: q1_points = 13, opponent_team_id = packers_id  
- Packers allowed: Query Cards stats where opponent_team_id = packers_id
"""

-- ============================
-- TEAM STATS TABLE
-- ============================

CREATE TABLE team_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    opponent_team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    
    -- Quarter by quarter scoring
    q1_points INTEGER DEFAULT 0,
    q2_points INTEGER DEFAULT 0,
    q3_points INTEGER DEFAULT 0, 
    q4_points INTEGER DEFAULT 0,
    ot_points INTEGER DEFAULT 0,  -- Overtime points if applicable
    final_score INTEGER DEFAULT 0,
    
    -- First downs breakdown
    first_downs_total INTEGER DEFAULT 0,
    first_downs_rush INTEGER DEFAULT 0,
    first_downs_pass INTEGER DEFAULT 0,
    first_downs_penalty INTEGER DEFAULT 0,
    
    -- Third down efficiency
    third_down_attempts INTEGER DEFAULT 0,
    third_down_conversions INTEGER DEFAULT 0,
    
    -- Time of possession (stored in seconds for precision)
    time_of_possession_seconds INTEGER DEFAULT 0,
    
    -- Total offense
    total_net_yards INTEGER DEFAULT 0,
    total_plays INTEGER DEFAULT 0,
    
    -- Rushing offense
    net_yards_rush INTEGER DEFAULT 0,
    rush_attempts INTEGER DEFAULT 0,
    
    -- Passing offense
    net_yards_pass INTEGER DEFAULT 0,
    pass_attempts INTEGER DEFAULT 0,
    pass_completions INTEGER DEFAULT 0,
    pass_interceptions_thrown INTEGER DEFAULT 0,
    
    -- Sacks (allowed by this team's offense)
    sacks_allowed INTEGER DEFAULT 0,
    sack_yards_lost INTEGER DEFAULT 0,
    
    -- Punting (by this team)
    punts INTEGER DEFAULT 0,
    punt_total_yards INTEGER DEFAULT 0,
    
    -- Return yards (by this team)
    return_yards_total INTEGER DEFAULT 0,
    punt_return_yards INTEGER DEFAULT 0,
    kickoff_return_yards INTEGER DEFAULT 0,
    
    -- Penalties (committed by this team)
    penalties INTEGER DEFAULT 0,
    penalty_yards INTEGER DEFAULT 0,
    
    -- Turnovers (committed by this team)
    fumbles INTEGER DEFAULT 0,
    fumbles_lost INTEGER DEFAULT 0,
    
    -- Additional computed fields
    yards_per_play DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN total_plays > 0 
        THEN CAST(total_net_yards AS FLOAT) / total_plays 
        ELSE 0 END
    ) STORED,
    
    yards_per_rush DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN rush_attempts > 0 
        THEN CAST(net_yards_rush AS FLOAT) / rush_attempts 
        ELSE 0 END
    ) STORED,
    
    pass_completion_pct DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN pass_attempts > 0 
        THEN CAST(pass_completions AS FLOAT) / pass_attempts * 100
        ELSE 0 END
    ) STORED,
    
    third_down_pct DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN third_down_attempts > 0 
        THEN CAST(third_down_conversions AS FLOAT) / third_down_attempts * 100
        ELSE 0 END
    ) STORED,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (opponent_team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Ensure one record per team per game
    UNIQUE(game_id, team_id),
    
    -- Data validation
    CHECK (q1_points >= 0 AND q2_points >= 0 AND q3_points >= 0 AND q4_points >= 0),
    CHECK (final_score >= 0),
    CHECK (first_downs_total >= 0),
    CHECK (third_down_conversions <= third_down_attempts),
    CHECK (pass_completions <= pass_attempts),
    CHECK (fumbles_lost <= fumbles),
    CHECK (team_id != opponent_team_id)
);

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================

CREATE INDEX idx_team_stats_game ON team_stats(game_id);
CREATE INDEX idx_team_stats_team ON team_stats(team_id, season, week);
CREATE INDEX idx_team_stats_opponent ON team_stats(opponent_team_id, season, week);
CREATE INDEX idx_team_stats_season ON team_stats(league_id, season, week);
CREATE INDEX idx_team_stats_scoring ON team_stats(final_score DESC, total_net_yards DESC);

-- ============================
-- USEFUL VIEWS FOR QUERYING
-- ============================

-- Offensive stats view (what teams did)
CREATE VIEW team_offensive_stats AS
SELECT 
    ts.*,
    t.full_name as team_name,
    t.abbreviation as team_abbr,
    opp.full_name as opponent_name,
    opp.abbreviation as opponent_abbr,
    
    -- Game context
    g.game_type,
    g.day_of_week,
    g.game_status
    
FROM team_stats ts
JOIN teams t ON ts.team_id = t.team_id
JOIN teams opp ON ts.opponent_team_id = opp.team_id
JOIN games g ON ts.game_id = g.game_id;

-- Defensive stats view (what teams allowed)
CREATE VIEW team_defensive_stats AS
SELECT 
    ts.game_id,
    ts.opponent_team_id as team_id,  -- Flip perspective
    ts.team_id as opponent_team_id,
    ts.league_id,
    ts.season,
    ts.week,
    
    -- Points allowed by quarter
    ts.q1_points as q1_points_allowed,
    ts.q2_points as q2_points_allowed,
    ts.q3_points as q3_points_allowed,
    ts.q4_points as q4_points_allowed,
    ts.final_score as points_allowed,
    
    -- Yards allowed
    ts.total_net_yards as total_yards_allowed,
    ts.net_yards_rush as rush_yards_allowed,
    ts.net_yards_pass as pass_yards_allowed,
    
    -- Other defensive stats
    ts.first_downs_total as first_downs_allowed,
    ts.third_down_conversions as third_down_conversions_allowed,
    ts.third_down_attempts as third_down_attempts_allowed,
    
    -- Sacks made (sacks allowed by opponent)
    ts.sacks_allowed as sacks_made,
    ts.sack_yards_lost as sack_yards_gained,
    
    -- Turnovers forced
    ts.pass_interceptions_thrown as interceptions_made,
    ts.fumbles_lost as fumbles_recovered,
    
    -- Team names
    def_team.full_name as team_name,
    def_team.abbreviation as team_abbr,
    off_team.full_name as opponent_name,
    off_team.abbreviation as opponent_abbr
    
FROM team_stats ts
JOIN teams def_team ON ts.opponent_team_id = def_team.team_id  -- Defensive team
JOIN teams off_team ON ts.team_id = off_team.team_id;         -- Offensive team

-- Quarter scoring summary
CREATE VIEW quarter_scoring_summary AS
SELECT 
    ts.game_id,
    ts.season,
    ts.week,
    
    -- Team info
    t.full_name as team_name,
    opp.full_name as opponent_name,
    
    -- Quarter by quarter
    ts.q1_points,
    ts.q2_points, 
    ts.q3_points,
    ts.q4_points,
    ts.ot_points,
    ts.final_score,
    
    -- Game totals for context
    g.home_score,
    g.away_score,
    
    CASE WHEN ts.team_id = g.home_team_id THEN 'HOME' ELSE 'AWAY' END as venue
    
FROM team_stats ts
JOIN teams t ON ts.team_id = t.team_id
JOIN teams opp ON ts.opponent_team_id = opp.team_id
JOIN games g ON ts.game_id = g.game_id
ORDER BY ts.game_id, venue DESC;

-- Season totals view
CREATE VIEW team_season_totals AS
SELECT 
    team_id,
    league_id,
    season,
    t.full_name as team_name,
    
    -- Games played
    COUNT(*) as games_played,
    
    -- Scoring totals
    SUM(final_score) as total_points_scored,
    AVG(final_score) as avg_points_per_game,
    SUM(q1_points) as total_q1_points,
    SUM(q2_points) as total_q2_points,
    SUM(q3_points) as total_q3_points,
    SUM(q4_points) as total_q4_points,
    
    -- Yardage totals
    SUM(total_net_yards) as total_net_yards,
    AVG(total_net_yards) as avg_yards_per_game,
    SUM(net_yards_rush) as total_rush_yards,
    SUM(net_yards_pass) as total_pass_yards,
    
    -- Efficiency
    AVG(yards_per_play) as avg_yards_per_play,
    AVG(third_down_pct) as avg_third_down_pct,
    
    -- Turnovers
    SUM(pass_interceptions_thrown) as total_interceptions_thrown,
    SUM(fumbles_lost) as total_fumbles_lost,
    
    -- Time of possession (convert to average per game in MM:SS format)
    AVG(time_of_possession_seconds) as avg_time_of_possession_seconds
    
FROM team_stats ts
JOIN teams t ON ts.team_id = t.team_id
GROUP BY team_id, league_id, season
ORDER BY season, total_points_scored DESC;

-- ============================
-- EXAMPLE QUERIES
-- ============================

/*
-- Example 1: Cards Q1 scoring vs Packers
SELECT q1_points 
FROM team_stats ts
JOIN teams t ON ts.team_id = t.team_id
JOIN teams opp ON ts.opponent_team_id = opp.team_id
WHERE t.team_name = 'Cards' AND opp.team_name = 'Packers'
  AND ts.season = 1 AND ts.week = 1;

-- Example 2: How many Q1 points did Packers allow and to whom?
SELECT 
    opp.full_name as scoring_team,
    ts.q1_points as points_allowed_q1
FROM team_stats ts
JOIN teams t ON ts.team_id = t.team_id
JOIN teams opp ON ts.opponent_team_id = opp.team_id  
WHERE opp.team_name = 'Packers'  -- Packers were the opponent (defense)
  AND ts.season = 1
ORDER BY ts.week;

-- Example 3: Team's quarterly scoring patterns
SELECT 
    team_name,
    AVG(q1_points) as avg_q1,
    AVG(q2_points) as avg_q2, 
    AVG(q3_points) as avg_q3,
    AVG(q4_points) as avg_q4
FROM team_season_totals tst
JOIN team_stats ts ON tst.team_id = ts.team_id AND tst.season = ts.season
GROUP BY team_name, tst.season;

-- Example 4: Best/worst defenses by points allowed per quarter
SELECT 
    team_name,
    AVG(q1_points_allowed) as avg_q1_allowed,
    AVG(points_allowed) as avg_total_allowed
FROM team_defensive_stats
WHERE season = 1
GROUP BY team_id, team_name
ORDER BY avg_total_allowed;
*/
