CREATE TABLE games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    
    -- Game type and structure
    game_type VARCHAR(20) NOT NULL DEFAULT 'REGULAR'
        CHECK (game_type IN ('PRESEASON', 'REGULAR', 'WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL')),
    
    -- Teams
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    
    -- Scheduling (date/time optional since week drives it)
    game_date DATE,                    -- Optional: actual calendar date
    game_time TIME,                    -- Optional: kickoff time
    day_of_week VARCHAR(10),           -- 'Thursday', 'Sunday', 'Monday', etc.
    
    -- Game status and results
    game_status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED'
        CHECK (game_status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'POSTPONED', 'CANCELLED')),
    
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    
    -- Playoff specific fields (NULL for regular season)
    playoff_round INTEGER,             -- 1=Wildcard, 2=Divisional, 3=Conference, 4=Superbowl
    playoff_game_number INTEGER,      -- Game number within the round
    playoff_bracket_position VARCHAR(10), -- 'AFC-1', 'NFC-2', etc.
    
    -- Game details
    game_notes TEXT,                   -- 'TNF', 'MNF', 'SNF', 'International', etc.
    weather_conditions TEXT,           -- For outdoor games
    attendance INTEGER,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (home_team_id != away_team_id),  -- Team can't play itself
    CHECK (home_score >= 0 AND away_score >= 0),
    CHECK (week >= 1 AND week <= 25),     -- Allows for extended playoffs
    CHECK (playoff_round IS NULL OR playoff_round BETWEEN 1 AND 4)
);

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================

CREATE INDEX idx_games_schedule ON games(league_id, season, week, game_type);
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX idx_games_status ON games(game_status, season, week);
CREATE INDEX idx_games_playoffs ON games(season, playoff_round, playoff_game_number);
CREATE INDEX idx_games_date ON games(game_date, game_time);

