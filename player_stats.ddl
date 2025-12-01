# ========================================
# database/player_stats.sql
# Version: 1.0
# ========================================

"""
Player Statistics Table

Stores comprehensive individual player statistics for each game, tracking
performance against specific opponents. Each player gets one record per game
with all their statistical categories, allowing queries like "How did Player X
perform against Team Y?" or "How many yards did Team Z allow to opposing RBs?"

Example: Mark Ingram catches 7 passes for 108 yards vs Redskins
- Record: player_id=ingram, opponent=redskins, receiving_catches=7, receiving_yards=108
"""

-- ============================
-- PLAYER STATS TABLE
-- ============================

drop table player_stats;
CREATE TABLE player_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    opponent_team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    
    -- Player position for this game (may differ from primary position)
    position_played VARCHAR(5),
    jersey_number INTEGER,
    
    -- RUSHING STATISTICS
    rushing_attempts INTEGER DEFAULT 0,
    rushing_yards INTEGER DEFAULT 0,
    rushing_touchdowns INTEGER DEFAULT 0,
    rushing_longest INTEGER DEFAULT 0,
    
    -- PASSING STATISTICS  
    passing_attempts INTEGER DEFAULT 0,
    passing_completions INTEGER DEFAULT 0,
    passing_yards INTEGER DEFAULT 0,
    passing_touchdowns INTEGER DEFAULT 0,
    passing_interceptions INTEGER DEFAULT 0,
    passing_longest INTEGER DEFAULT 0,
    
    -- RECEIVING STATISTICS
    receiving_catches INTEGER DEFAULT 0,
    receiving_yards INTEGER DEFAULT 0,
    receiving_touchdowns INTEGER DEFAULT 0,
    receiving_longest INTEGER DEFAULT 0,
    
    -- DEFENSIVE STATISTICS
    sacks DECIMAL(2,1) DEFAULT 0.0,  -- Allow half sacks
    interceptions INTEGER DEFAULT 0,
    interception_yards INTEGER DEFAULT 0,
    interception_touchdowns INTEGER DEFAULT 0,
    interception_longest INTEGER DEFAULT 0,
    
    -- SPECIAL TEAMS - KICKING
    extra_points_attempted INTEGER DEFAULT 0,
    extra_points_made INTEGER DEFAULT 0,
    field_goals_attempted INTEGER DEFAULT 0,
    field_goals_made INTEGER DEFAULT 0,
    field_goal_longest INTEGER DEFAULT 0,
    
    punt_returns INTEGER DEFAULT 0,
    punt_return_yards INTEGER DEFAULT 0,
    punt_return_touchdowns INTEGER DEFAULT 0,
    punt_return_longest INTEGER DEFAULT 0,

    kickoff_returns INTEGER DEFAULT 0,
    kickoff_return_yards INTEGER DEFAULT 0,
    kickoff_return_touchdowns INTEGER DEFAULT 0,
    kickoff_return_longest INTEGER DEFAULT 0,
    
    -- Computed averages (stored for performance)
    rushing_average DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN rushing_attempts > 0 
        THEN CAST(rushing_yards AS FLOAT) / rushing_attempts 
        ELSE 0 END
    ) STORED,
    
    passing_completion_pct DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN passing_attempts > 0 
        THEN CAST(passing_completions AS FLOAT) / passing_attempts * 100
        ELSE 0 END
    ) STORED,
    
    receiving_average DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN receiving_catches > 0 
        THEN CAST(receiving_yards AS FLOAT) / receiving_catches 
        ELSE 0 END
    ) STORED,
    
    kickoff_return_average DECIMAL(4,2) GENERATED ALWAYS AS (
        CASE WHEN kickoff_returns > 0 
        THEN CAST(kickoff_return_yards AS FLOAT) / kickoff_returns 
        ELSE 0 END
    ) STORED,
    
    field_goal_pct DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN field_goals_attempted > 0 
        THEN CAST(field_goals_made AS FLOAT) / field_goals_attempted * 100
        ELSE 0 END
    ) STORED,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (opponent_team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Ensure one record per player per game
    UNIQUE(game_id, player_id),
    
    -- Data validation constraints
    --CHECK (rushing_attempts >= 0 AND rushing_yards >= 0),
    CHECK (passing_completions <= passing_attempts),
    --CHECK (receiving_catches >= 0 AND receiving_yards >= 0),
    CHECK (extra_points_made <= extra_points_attempted),
    CHECK (field_goals_made <= field_goals_attempted),
    CHECK (sacks >= 0),
    CHECK (team_id != opponent_team_id)
);

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================

CREATE INDEX idx_player_stats_game ON player_stats(game_id);
CREATE INDEX idx_player_stats_player ON player_stats(player_id, season, week);
CREATE INDEX idx_player_stats_team ON player_stats(team_id, season, week);
CREATE INDEX idx_player_stats_opponent ON player_stats(opponent_team_id, season, week);
CREATE INDEX idx_player_stats_position ON player_stats(position_played, season);
CREATE INDEX idx_player_stats_performance ON player_stats(rushing_yards DESC, receiving_yards DESC, passing_yards DESC);

-- ============================
-- USEFUL VIEWS FOR QUERYING
-- ============================

-- Complete player game stats with names
drop view player_game_stats;
CREATE VIEW player_game_stats AS
SELECT 
    ps.*,
    p.display_name as player_name,
    p.position as primary_position,
    team.full_name as team_name,
    team.abbreviation as team_abbr,
    opp.full_name as opponent_name,
    opp.abbreviation as opponent_abbr,
    g.game_type,
    g.day_of_week,
    g.game_status
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
JOIN games g ON ps.game_id = g.game_id;

-- Rushing statistics view
drop view player_rushing_stats;
CREATE VIEW player_rushing_stats AS
SELECT 
    ps.game_id,
    ps.season,
    ps.week,
    p.display_name as player_name,
    p.jersey_number,
    ps.position_played,
    team.full_name as team_name,
    opp.full_name as opponent_name,
    ps.rushing_attempts,
    ps.rushing_yards,
    ps.rushing_average,
    ps.rushing_longest,
    ps.rushing_touchdowns
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
WHERE ps.rushing_attempts > 0
ORDER BY ps.rushing_yards DESC;

-- Passieng statistics view
drop view player_passing_stats;
CREATE VIEW player_passing_stats AS
SELECT 
    ps.game_id,
    ps.season,
    ps.week,
    p.display_name as player_name,
    p.jersey_number,
    ps.position_played,
    team.full_name as team_name,
    opp.full_name as opponent_name,
    ps.passing_attempts,
    ps.passing_completions,
    ps.passing_completion_pct,
    ps.passing_yards,
    ps.passing_touchdowns,
    ps.passing_interceptions,
    ps.passing_longest
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
WHERE ps.passing_attempts > 0
ORDER BY ps.passing_yards DESC;

-- Receiving statistics view
drop view player_receiving_stats;
CREATE VIEW player_receiving_stats AS
SELECT 
    ps.game_id,
    ps.season,
    ps.week,
    p.display_name as player_name,
    p.jersey_number,
    ps.position_played,
    team.full_name as team_name,
    opp.full_name as opponent_name,
    ps.receiving_catches,
    ps.receiving_yards,
    ps.receiving_average,
    ps.receiving_longest,
    ps.receiving_touchdowns
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
WHERE ps.receiving_catches > 0
ORDER BY ps.receiving_yards DESC;

-- Defensive statistics view
drop view player_defensive_stats;
CREATE VIEW player_defensive_stats AS
SELECT 
    ps.game_id,
    ps.season,
    ps.week,
    p.display_name as player_name,
    p.jersey_number,
    ps.position_played,
    team.full_name as team_name,
    opp.full_name as opponent_name,
    ps.sacks,
    ps.interceptions,
    ps.interception_yards,
    ps.interception_touchdowns,
    ps.interception_longest
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
WHERE (ps.sacks > 0 OR ps.interceptions > 0 
       OR ps.fumbles_forced > 0 OR ps.fumbles_recovered > 0)
ORDER BY ps.sacks DESC;

-- Season totals by player
drop view player_season_totals;
CREATE VIEW player_season_totals AS
SELECT 
    ps.player_id,
    p.display_name as player_name,
    p.position as primary_position,
    ps.team_id,
    team.full_name as team_name,
    ps.season,
    ps.league_id,
    
    -- Games played
    COUNT(*) as games_played,
    
    -- Rushing totals
    SUM(ps.rushing_attempts) as total_rushing_attempts,
    SUM(ps.rushing_yards) as total_rushing_yards,
    SUM(ps.rushing_touchdowns) as total_rushing_touchdowns,
    MAX(ps.rushing_longest) as longest_rush,
    CASE WHEN SUM(ps.rushing_attempts) > 0 
         THEN ROUND(CAST(SUM(ps.rushing_yards) AS FLOAT) / SUM(ps.rushing_attempts), 2)
         ELSE 0 END as season_rushing_avg,
    
    -- Passing totals
    SUM(ps.passing_attempts) as total_passing_attempts,
    SUM(ps.passing_completions) as total_passing_completions,
    SUM(ps.passing_yards) as total_passing_yards,
    SUM(ps.passing_touchdowns) as total_passing_touchdowns,
    SUM(ps.passing_interceptions) as total_passing_interceptions,
    MAX(ps.passing_longest) as longest_pass,
    CASE WHEN SUM(ps.passing_attempts) > 0 
         THEN ROUND(CAST(SUM(ps.passing_completions) AS FLOAT) / SUM(ps.passing_attempts) * 100, 2)
         ELSE 0 END as season_completion_pct,
    
    -- Receiving totals
    SUM(ps.receiving_catches) as total_receiving_catches,
    SUM(ps.receiving_yards) as total_receiving_yards,
    SUM(ps.receiving_touchdowns) as total_receiving_touchdowns,
    MAX(ps.receiving_longest) as longest_reception,
    CASE WHEN SUM(ps.receiving_catches) > 0 
         THEN ROUND(CAST(SUM(ps.receiving_yards) AS FLOAT) / SUM(ps.receiving_catches), 2)
         ELSE 0 END as season_receiving_avg,
    
    -- Defensive totals
    SUM(ps.sacks) as total_sacks,
    SUM(ps.interceptions) as total_interceptions,
    SUM(ps.interception_yards) as total_interception_yards,
    
    -- Special teams totals
    SUM(ps.field_goals_made) as total_field_goals_made,
    SUM(ps.field_goals_attempted) as total_field_goals_attempted,
    SUM(ps.kickoff_return_yards) as total_kickoff_return_yards
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams team ON ps.team_id = team.team_id
GROUP BY ps.player_id, ps.season, ps.team_id
ORDER BY ps.season, total_rushing_yards DESC, total_receiving_yards DESC, total_passing_yards DESC;

-- Opponent-specific performance view
drop view player_vs_opponent_stats;
CREATE VIEW player_vs_opponent_stats AS
SELECT 
    ps.player_id,
    p.display_name as player_name,
    ps.opponent_team_id,
    opp.full_name as opponent_name,
    ps.season,
    
    -- Games against this opponent
    COUNT(*) as games_vs_opponent,
    
    -- Performance vs this opponent
    SUM(ps.rushing_yards) as rush_yards_vs_opponent,
    SUM(ps.receiving_yards) as rec_yards_vs_opponent,
    SUM(ps.passing_yards) as pass_yards_vs_opponent,
    SUM(ps.rushing_touchdowns + ps.receiving_touchdowns + ps.passing_touchdowns) as total_tds_vs_opponent,
    
    -- Averages
    AVG(ps.rushing_yards) as avg_rush_yards_vs_opponent,
    AVG(ps.receiving_yards) as avg_rec_yards_vs_opponent,
    AVG(ps.passing_yards) as avg_pass_yards_vs_opponent
    
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
GROUP BY ps.player_id, ps.opponent_team_id, ps.season
HAVING (SUM(ps.rushing_yards) > 0 OR SUM(ps.receiving_yards) > 0 OR SUM(ps.passing_yards) > 0)
ORDER BY ps.season, total_tds_vs_opponent DESC;

-- ============================
-- EXAMPLE QUERIES
-- ============================

/*
-- Example 1: Mark Ingram's performance vs Redskins
SELECT 
    player_name,
    opponent_name,
    receiving_catches,
    receiving_yards,
    receiving_average,
    receiving_touchdowns
FROM player_receiving_stats 
WHERE player_name LIKE '%Ingram%' 
  AND opponent_name LIKE '%Redskins%'
  AND season = 1;

-- Example 2: How many receiving yards did Giants allow to opposing RBs?
SELECT 
    p.display_name as receiver,
    ps.receiving_catches,
    ps.receiving_yards,
    ps.receiving_touchdowns
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams opp ON ps.opponent_team_id = opp.team_id
WHERE opp.team_name = 'Giants'
  AND ps.position_played = 'RB'
  AND ps.receiving_catches > 0
  AND ps.season = 1
ORDER BY ps.receiving_yards DESC;

-- Example 3: QB performance vs specific defenses
SELECT 
    player_name,
    opponent_name,
    passing_attempts,
    passing_completions,
    passing_completion_pct,
    passing_yards,
    passing_touchdowns,
    passing_interceptions
FROM player_passing_stats
WHERE season = 1
ORDER BY passing_yards DESC;

-- Example 4: Season leaders by category
SELECT 
    player_name,
    team_name,
    total_rushing_yards,
    total_receiving_yards,
    total_passing_yards
FROM player_season_totals
WHERE season = 1
ORDER BY total_rushing_yards DESC
LIMIT 10;

-- Example 5: Player's best games vs toughest opponents
SELECT 
    player_name,
    opponent_name,
    games_vs_opponent,
    rush_yards_vs_opponent,
    rec_yards_vs_opponent,
    total_tds_vs_opponent
FROM player_vs_opponent_stats
WHERE player_name LIKE '%Ingram%'
ORDER BY total_tds_vs_opponent DESC;
*/
