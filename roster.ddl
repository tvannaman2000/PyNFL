-- ============================
-- ROSTER TABLE - Current Team Assignments
-- ============================

CREATE TABLE roster (
    roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL, -- Denormalized for performance
    
    -- Roster details
    jersey_number INTEGER,
    roster_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (roster_status IN ('ACTIVE', 'PRACTICE_SQUAD', 'INJURED_RESERVE', 'SUSPENDED')),
    
    -- Contract/Assignment info (keep simple for now)
    signed_date DATE NOT NULL DEFAULT CURRENT_DATE,
    contract_years INTEGER DEFAULT 1,
    
    -- Position on this team (can differ from player's primary position)
    position_on_team_id INTEGER,  
    position_on_team VARCHAR(5), -- NULL = use player's primary position
    
    -- Depth chart info
    depth_chart_order INTEGER, -- 1 = starter, 2 = backup, etc.
    
    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (position_on_team_id) REFERENCES positions(position_id)

    
    -- Constraints
    -- UNIQUE(team_id, jersey_number, is_active) -- No duplicate jersey numbers per team
);

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_roster_player ON roster(player_id, is_active);
CREATE INDEX idx_roster_team ON roster(team_id, is_active);
CREATE INDEX idx_roster_league ON roster(league_id, is_active);
CREATE INDEX idx_roster_position ON roster(position_on_team_id, depth_chart_order);
