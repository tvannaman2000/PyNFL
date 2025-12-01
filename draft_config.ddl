-- ============================
-- DRAFT CONFIGURATION TABLE
-- ============================

CREATE TABLE draft_configuration (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    
    -- Draft structure
    draft_rounds INTEGER NOT NULL DEFAULT 7
        CHECK (draft_rounds >= 3 AND draft_rounds <= 12),
    draft_order_method VARCHAR(20) NOT NULL DEFAULT 'WORST_TO_BEST'
        CHECK (draft_order_method IN ('WORST_TO_BEST', 'RANDOM', 'CUSTOM')),
    enable_compensatory_picks BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Prospect generation
    prospects_per_round INTEGER NOT NULL DEFAULT 10
        CHECK (prospects_per_round >= 5 AND prospects_per_round <= 20),
    quality_variation INTEGER NOT NULL DEFAULT 5
        CHECK (quality_variation >= 1 AND quality_variation <= 10),
    auto_generate_prospects BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Draft rules
    allow_pick_trading BOOLEAN NOT NULL DEFAULT TRUE,
    create_undrafted_fa BOOLEAN NOT NULL DEFAULT TRUE,
    enable_draft_timer BOOLEAN NOT NULL DEFAULT FALSE,
    draft_timer_minutes INTEGER DEFAULT 5
        CHECK (draft_timer_minutes IS NULL OR (draft_timer_minutes >= 1 AND draft_timer_minutes <= 60)),
    
    -- Draft execution settings
    current_draft_year INTEGER,
    draft_status VARCHAR(20) DEFAULT 'NOT_STARTED'
        CHECK (draft_status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PAUSED')),
    current_round INTEGER DEFAULT 1,
    current_pick INTEGER DEFAULT 1,
    
    -- Advanced settings
    salary_cap_impact BOOLEAN DEFAULT FALSE,
    rookie_contract_years INTEGER DEFAULT 4
        CHECK (rookie_contract_years >= 1 AND rookie_contract_years <= 7),
    
    -- Metadata
    configuration_name VARCHAR(50) NOT NULL DEFAULT 'Standard Draft Rules',
    description TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Ensure only one active config per league
    UNIQUE(league_id, is_active)
);

-- ============================
-- DRAFT ORDER TABLE - Stores the actual draft order
-- ============================

CREATE TABLE draft_order (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    draft_year INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    pick_number INTEGER NOT NULL,  -- Overall pick number (1, 2, 3...)
    pick_in_round INTEGER NOT NULL, -- Pick within the round (1-32, 1-32, etc.)
    team_id INTEGER NOT NULL,
    
    -- Pick details
    is_compensatory BOOLEAN DEFAULT FALSE,
    is_traded BOOLEAN DEFAULT FALSE,
    original_team_id INTEGER,  -- If traded, who originally owned it
    trade_notes TEXT,
    
    -- Player selected (NULL until pick is made)
    selected_player_id INTEGER,
    selected_prospect_id INTEGER,
    pick_status VARCHAR(20) DEFAULT 'AVAILABLE'
        CHECK (pick_status IN ('AVAILABLE', 'SELECTED', 'TRADED', 'FORFEITED')),
    
    -- Timing
    pick_time DATETIME,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (original_team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (selected_player_id) REFERENCES players(player_id) ON DELETE SET NULL,
    FOREIGN KEY (selected_prospect_id) REFERENCES draft_prospects(prospect_id) ON DELETE SET NULL,
    
    UNIQUE(league_id, draft_year, pick_number),
    UNIQUE(league_id, draft_year, round_number, pick_in_round)
);

-- ============================
-- DEFAULT CONFIGURATION INSERT
-- ============================

-- Insert default draft configuration for existing leagues
INSERT INTO draft_configuration (
    league_id, configuration_name, description,
    draft_rounds, draft_order_method, enable_compensatory_picks,
    prospects_per_round, quality_variation, auto_generate_prospects,
    allow_pick_trading, create_undrafted_fa, enable_draft_timer
) 
SELECT 
    league_id, 'Standard Draft Rules', 'Default NFL-style draft configuration',
    7, 'WORST_TO_BEST', FALSE,  -- Draft structure
    10, 5, TRUE,  -- Prospect generation
    TRUE, TRUE, FALSE  -- Draft rules
FROM leagues 
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM draft_configuration dc 
    WHERE dc.league_id = leagues.league_id
);

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_draft_config_league ON draft_configuration(league_id, is_active);
CREATE INDEX idx_draft_order_year ON draft_order(league_id, draft_year, pick_number);
CREATE INDEX idx_draft_order_team ON draft_order(team_id, draft_year);
CREATE INDEX idx_draft_order_status ON draft_order(draft_year, pick_status);

-- ============================
-- USEFUL VIEWS
-- ============================

CREATE VIEW league_draft_settings AS
SELECT 
    l.league_id,
    l.league_name,
    dc.configuration_name,
    dc.draft_rounds,
    dc.draft_order_method,
    dc.enable_compensatory_picks,
    dc.prospects_per_round,
    dc.quality_variation,
    dc.auto_generate_prospects,
    dc.allow_pick_trading,
    dc.create_undrafted_fa,
    dc.enable_draft_timer,
    dc.current_draft_year,
    dc.draft_status
FROM leagues l
JOIN draft_configuration dc ON l.league_id = dc.league_id
WHERE l.is_active = TRUE AND dc.is_active = TRUE;

-- Current draft order view
CREATE VIEW current_draft_order AS
SELECT 
    do.*,
    t.full_name as team_name,
    t.abbreviation as team_abbr,
    ot.full_name as original_team_name,
    ot.abbreviation as original_team_abbr,
    p.display_name as selected_player_name,
    dp.display_name as selected_prospect_name
FROM draft_order do
JOIN teams t ON do.team_id = t.team_id
LEFT JOIN teams ot ON do.original_team_id = ot.team_id
LEFT JOIN players p ON do.selected_player_id = p.player_id
LEFT JOIN draft_prospects dp ON do.selected_prospect_id = dp.prospect_id
ORDER BY do.pick_number;
