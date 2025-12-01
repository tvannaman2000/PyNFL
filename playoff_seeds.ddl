
CREATE TABLE IF NOT EXISTS playoff_seeds (
    seed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    conference_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    seed_number INTEGER NOT NULL,  -- 1-7 (or however many playoff teams)
    
    -- Seeding details
    is_division_winner BOOLEAN NOT NULL DEFAULT FALSE,
    division_id INTEGER,
    seed_type VARCHAR(20) NOT NULL,  -- 'Division Winner' or 'Wild Card'
    
    -- Team record at time of seeding
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    ties INTEGER NOT NULL DEFAULT 0,
    win_pct REAL NOT NULL DEFAULT 0.0,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (conference_id) REFERENCES conferences(conference_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES divisions(division_id) ON DELETE SET NULL,
    
    -- Constraints
    UNIQUE(league_id, season, conference_id, seed_number),  -- Each seed # unique per conference
    UNIQUE(league_id, season, team_id),  -- Each team can only have one seed
    CHECK (seed_number >= 1 AND seed_number <= 16)  -- Reasonable range
);

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_playoff_seeds_lookup ON playoff_seeds(league_id, season, conference_id);
CREATE INDEX idx_playoff_seeds_team ON playoff_seeds(team_id, season);

-- ============================
-- VIEWS
-- ============================

-- View showing playoff bracket with team details
CREATE VIEW playoff_seeding AS
SELECT 
    ps.seed_id,
    ps.league_id,
    ps.season,
    ps.seed_number,
    ps.seed_type,
    ps.is_division_winner,
    
    -- Conference info
    c.conference_name,
    c.abbreviation as conference_abbr,
    
    -- Team info
    t.team_id,
    t.full_name as team_name,
    t.abbreviation as team_abbr,
    
    -- Division info
    d.division_name,
    
    -- Record
    ps.wins,
    ps.losses,
    ps.ties,
    ps.win_pct,
    
    ps.created_date
    
FROM playoff_seeds ps
JOIN conferences c ON ps.conference_id = c.conference_id
JOIN teams t ON ps.team_id = t.team_id
LEFT JOIN divisions d ON ps.division_id = d.division_id
ORDER BY ps.season, c.conference_name, ps.seed_number;

-- ============================
-- COMMENTS
-- ============================

/*
USAGE NOTES:

1. This table is populated when Wild Card round is generated
2. Seeds are locked and don't change even if playoff games are played
3. If Wild Card is regenerated, old seeds are deleted and new ones inserted
4. Later playoff rounds use this table instead of recalculating from standings

EXAMPLE QUERIES:

-- Get all seeds for a season
SELECT * FROM playoff_seeding WHERE season = 1 ORDER BY conference_name, seed_number;

-- Get seeds for a specific conference
SELECT * FROM playoff_seeding 
WHERE season = 1 AND conference_abbr = 'AFC' 
ORDER BY seed_number;

-- Check if seeds exist for a season
SELECT COUNT(*) FROM playoff_seeds WHERE league_id = 1 AND season = 1;

-- Delete seeds for regeneration
DELETE FROM playoff_seeds WHERE league_id = 1 AND season = 1;
*/
