-- ============================
-- COACHES TABLE - Head coaches and their philosophies
-- ============================

CREATE TABLE coaches (
    coach_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    
    -- Identity
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    display_name VARCHAR(50) GENERATED ALWAYS AS (
        first_name || ' ' || last_name
    ) STORED,
    
    -- Coaching philosophies
    offensive_philosophy VARCHAR(12) NOT NULL DEFAULT 'BALANCED'
        CHECK (offensive_philosophy IN ('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE')),
    defensive_philosophy VARCHAR(12) NOT NULL DEFAULT 'BALANCED'
        CHECK (defensive_philosophy IN ('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE')),
    
    -- Experience and ratings
    years_experience INTEGER NOT NULL DEFAULT 0,
    coaching_rating INTEGER DEFAULT 50 CHECK (coaching_rating >= 40 AND coaching_rating <= 99),
    
    -- Career totals (updated via triggers/procedures)
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,
    total_playoff_games INTEGER DEFAULT 0,
    total_playoff_wins INTEGER DEFAULT 0,
    total_playoff_losses INTEGER DEFAULT 0,
    
    -- Calculated fields
    win_percentage DECIMAL(5,3) GENERATED ALWAYS AS (
        CASE 
            WHEN total_games > 0 THEN CAST(total_wins AS DECIMAL) / total_games
            ELSE 0.000
        END
    ) STORED,
    
    playoff_win_percentage DECIMAL(5,3) GENERATED ALWAYS AS (
        CASE 
            WHEN total_playoff_games > 0 THEN CAST(total_playoff_wins AS DECIMAL) / total_playoff_games
            ELSE 0.000
        END
    ) STORED,
    
    -- Status
    coach_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (coach_status IN ('ACTIVE', 'RETIRED', 'FIRED', 'SUSPENDED')),
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (years_experience >= 0 AND years_experience <= 50),
    CHECK (total_games >= 0),
    CHECK (total_wins >= 0),
    CHECK (total_losses >= 0),
    CHECK (total_playoff_wins >= 0),
    CHECK (total_playoff_losses >= 0)
);

-- ============================
-- COACH HISTORY TABLE - Track coaching assignments and performance
-- ============================

CREATE TABLE coach_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    coach_id INTEGER NOT NULL,
    team_id INTEGER,  -- NULL for unemployment periods
    league_id INTEGER NOT NULL,
    
    -- Assignment period
    start_season INTEGER NOT NULL,
    end_season INTEGER,  -- NULL = current assignment
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,  -- NULL = current assignment
    
    -- Event type
    event_type VARCHAR(20) NOT NULL
        CHECK (event_type IN ('HIRED', 'FIRED', 'RESIGNED', 'RETIRED', 'SUSPENDED', 'SEASON_END')),
    
    -- Performance during this stint (updated periodically)
    games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    playoff_games INTEGER DEFAULT 0,
    playoff_wins INTEGER DEFAULT 0,
    playoff_losses INTEGER DEFAULT 0,
    
    -- Notes and details
    reason TEXT,  -- Why hired/fired/etc.
    contract_details TEXT,
    notes TEXT,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (coach_id) REFERENCES coaches(coach_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (start_season > 0),
    CHECK (end_season IS NULL OR end_season >= start_season),
    CHECK (games >= 0),
    CHECK (wins >= 0),
    CHECK (losses >= 0),
    CHECK (ties >= 0),
    CHECK (wins + losses + ties <= games),
    CHECK (playoff_games >= 0),
    CHECK (playoff_wins >= 0),
    CHECK (playoff_losses >= 0),
    CHECK (playoff_wins + playoff_losses <= playoff_games)
);

-- ============================
-- UPDATE TEAMS TABLE - Add current coach reference
-- ============================

-- Add coach reference to teams table
ALTER TABLE teams ADD COLUMN current_coach_id INTEGER;
ALTER TABLE teams ADD CONSTRAINT fk_teams_coach 
    FOREIGN KEY (current_coach_id) REFERENCES coaches(coach_id) ON DELETE SET NULL;

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================

CREATE INDEX idx_coaches_league ON coaches(league_id, coach_status);
CREATE INDEX idx_coaches_status ON coaches(coach_status);
CREATE INDEX idx_coaches_rating ON coaches(coaching_rating DESC);
CREATE INDEX idx_coaches_experience ON coaches(years_experience DESC);

CREATE INDEX idx_coach_history_coach ON coach_history(coach_id, start_season);
CREATE INDEX idx_coach_history_team ON coach_history(team_id, start_season, end_season);
CREATE INDEX idx_coach_history_season ON coach_history(league_id, start_season, end_season);
CREATE INDEX idx_coach_history_event ON coach_history(event_type, start_date);

CREATE INDEX idx_teams_coach ON teams(current_coach_id);

-- ============================
-- USEFUL VIEWS
-- ============================

-- Current coaching assignments
CREATE VIEW current_coaching_assignments AS
SELECT 
    c.coach_id,
    c.display_name as coach_name,
    c.offensive_philosophy,
    c.defensive_philosophy,
    c.coaching_rating,
    c.years_experience,
    c.win_percentage,
    
    t.team_id,
    t.full_name as team_name,
    t.abbreviation as team_abbr,
    
    ch.start_season,
    ch.start_date,
    ch.games as current_stint_games,
    ch.wins as current_stint_wins,
    ch.losses as current_stint_losses
    
FROM coaches c
JOIN teams t ON c.coach_id = t.current_coach_id
LEFT JOIN coach_history ch ON c.coach_id = ch.coach_id 
    AND ch.team_id = t.team_id 
    AND ch.end_season IS NULL
WHERE c.coach_status = 'ACTIVE'
  AND t.is_active = TRUE;

-- Available coaches (not currently assigned)
CREATE VIEW available_coaches AS
SELECT 
    c.coach_id,
    c.display_name,
    c.offensive_philosophy,
    c.defensive_philosophy,
    c.coaching_rating,
    c.years_experience,
    c.total_games,
    c.win_percentage,
    c.coach_status,
    
    -- Last team coached
    (SELECT t.full_name 
     FROM coach_history ch2 
     JOIN teams t ON ch2.team_id = t.team_id 
     WHERE ch2.coach_id = c.coach_id 
     ORDER BY ch2.end_date DESC 
     LIMIT 1) as last_team_coached,
     
    -- When last coached
    (SELECT ch2.end_date 
     FROM coach_history ch2 
     WHERE ch2.coach_id = c.coach_id 
     ORDER BY ch2.end_date DESC 
     LIMIT 1) as last_coached_date
     
FROM coaches c
WHERE c.coach_status = 'ACTIVE'
  AND c.coach_id NOT IN (
    SELECT t.current_coach_id 
    FROM teams t 
    WHERE t.current_coach_id IS NOT NULL 
      AND t.is_active = TRUE
  );

-- Coaching performance summary
CREATE VIEW coaching_performance_summary AS
SELECT 
    c.coach_id,
    c.display_name,
    c.years_experience,
    c.coaching_rating,
    c.total_games,
    c.total_wins,
    c.total_losses,
    c.win_percentage,
    c.total_playoff_games,
    c.playoff_win_percentage,
    
    -- Count of teams coached
    COUNT(DISTINCT ch.team_id) as teams_coached,
    
    -- Best season record
    MAX(CASE WHEN ch.games > 0 THEN 
        CAST(ch.wins AS DECIMAL) / ch.games 
        ELSE 0 END) as best_season_win_pct
        
FROM coaches c
LEFT JOIN coach_history ch ON c.coach_id = ch.coach_id
GROUP BY c.coach_id, c.display_name, c.years_experience, c.coaching_rating,
         c.total_games, c.total_wins, c.total_losses, c.win_percentage,
         c.total_playoff_games, c.playoff_win_percentage;
