-- ============================
-- PLAYER HISTORY TABLE - Track all player movements and changes
-- ============================

CREATE TABLE player_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    
    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL 
        CHECK (transaction_type IN (
            'DRAFTED', 'SIGNED', 'TRADED', 'RELEASED', 'WAIVED', 
            'RETIRED', 'INJURED_RESERVE', 'SUSPENDED', 'SKILL_UPDATE',
            'POSITION_CHANGE', 'JERSEY_CHANGE'
        )),
    
    -- Team involvement
    from_team_id INTEGER, -- NULL for draft/free agent signing
    to_team_id INTEGER,   -- NULL for release/retirement
    
    -- Transaction context
    season INTEGER NOT NULL,
    week INTEGER, -- NULL for off-season moves
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Additional details (JSON-like text field for flexibility)
    details TEXT, -- Store specific info like "Round 2, Pick 15" for draft
    
    -- Skill changes (if transaction_type = 'SKILL_UPDATE')
    skill_changes TEXT, -- JSON: {"skill_run": {"old": 75, "new": 78}}
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (from_team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (to_team_id) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_player_history_player ON player_history(player_id, season);
CREATE INDEX idx_player_history_season ON player_history(league_id, season, transaction_type);
CREATE INDEX idx_player_history_teams ON player_history(from_team_id, to_team_id);
CREATE INDEX idx_player_history_type ON player_history(transaction_type, transaction_date);
