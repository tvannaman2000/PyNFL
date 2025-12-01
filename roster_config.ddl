-- ============================
-- ROSTER CONFIGURATION TABLE
-- ============================

CREATE TABLE roster_configuration (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    
    -- Basic roster sizes
    active_roster_size INTEGER NOT NULL DEFAULT 53,
    injured_reserve_size INTEGER NOT NULL DEFAULT 10,
    practice_squad_size INTEGER NOT NULL DEFAULT 16,
    
    -- Position minimums (required on active roster)
    min_qb INTEGER NOT NULL DEFAULT 1,
    min_rb INTEGER NOT NULL DEFAULT 1,
    min_fb INTEGER NOT NULL DEFAULT 0,
    min_wr INTEGER NOT NULL DEFAULT 3,
    min_te INTEGER NOT NULL DEFAULT 1,
    min_ol INTEGER NOT NULL DEFAULT 5,  -- Total offensive line
    min_dl INTEGER NOT NULL DEFAULT 4,  -- Total defensive line  
    min_lb INTEGER NOT NULL DEFAULT 3,  -- Total linebackers
    min_db INTEGER NOT NULL DEFAULT 4,  -- Total defensive backs
    min_k INTEGER NOT NULL DEFAULT 1,
    min_p INTEGER NOT NULL DEFAULT 1,
    
    -- Position maximums (prevent roster imbalance)
    max_qb INTEGER NOT NULL DEFAULT 4,
    max_rb INTEGER NOT NULL DEFAULT 8,
    max_fb INTEGER NOT NULL DEFAULT 3,
    max_wr INTEGER NOT NULL DEFAULT 12,
    max_te INTEGER NOT NULL DEFAULT 6,
    max_ol INTEGER NOT NULL DEFAULT 15,
    max_dl INTEGER NOT NULL DEFAULT 12,
    max_lb INTEGER NOT NULL DEFAULT 10,
    max_db INTEGER NOT NULL DEFAULT 12,
    max_k INTEGER NOT NULL DEFAULT 2,
    max_p INTEGER NOT NULL DEFAULT 2,
    
    -- Roster management rules
    allow_position_changes BOOLEAN DEFAULT TRUE,
    require_depth_chart BOOLEAN DEFAULT TRUE,
    auto_assign_jersey_numbers BOOLEAN DEFAULT FALSE,
    enforce_jersey_by_position BOOLEAN DEFAULT TRUE,
    
    -- Injury/status rules
    max_ir_weeks INTEGER DEFAULT 8,        -- Max weeks on IR before forced retirement
    allow_ir_return BOOLEAN DEFAULT TRUE,   -- Can players return from IR?
    max_suspended_weeks INTEGER DEFAULT 17, -- Max suspension length
    
    -- Contract/salary rules (for future expansion)
    enable_salary_cap BOOLEAN DEFAULT FALSE,
    salary_cap_amount INTEGER DEFAULT 0,
    enable_contracts BOOLEAN DEFAULT FALSE,
    max_contract_years INTEGER DEFAULT 7,
    
    -- Metadata
    configuration_name VARCHAR(50) DEFAULT 'Standard NFL Rules',
    description TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    
    -- Ensure roster sizes make sense
    CHECK (active_roster_size > 0 AND active_roster_size <= 100),
    CHECK (injured_reserve_size >= 0 AND injured_reserve_size <= 50),
    CHECK (practice_squad_size >= 0 AND practice_squad_size <= 30),
    
    -- Ensure minimums don't exceed maximums
    CHECK (min_qb <= max_qb),
    CHECK (min_rb <= max_rb),
    CHECK (min_fb <= max_fb),
    CHECK (min_wr <= max_wr),
    CHECK (min_te <= max_te),
    CHECK (min_ol <= max_ol),
    CHECK (min_dl <= max_dl),
    CHECK (min_lb <= max_lb),
    CHECK (min_db <= max_db),
    CHECK (min_k <= max_k),
    CHECK (min_p <= max_p)
);

-- ============================
-- DEFAULT CONFIGURATION INSERT
-- ============================

-- Insert default NFL-style configuration for existing leagues
INSERT INTO roster_configuration (
    league_id, configuration_name, description,
    active_roster_size, injured_reserve_size, practice_squad_size,
    min_qb, min_rb, min_fb, min_wr, min_te, min_ol, min_dl, min_lb, min_db, min_k, min_p,
    max_qb, max_rb, max_fb, max_wr, max_te, max_ol, max_dl, max_lb, max_db, max_k, max_p
) 
SELECT 
    league_id, 'Standard NFL Rules', 'Default NFL-style roster configuration',
    53, 10, 16,  -- Roster sizes
    1, 1, 0, 3, 1, 5, 4, 3, 4, 1, 1,  -- Minimums
    4, 8, 3, 12, 6, 15, 12, 10, 12, 2, 2  -- Maximums
FROM leagues 
WHERE is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM roster_configuration rc 
    WHERE rc.league_id = leagues.league_id
);

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_roster_config_league ON roster_configuration(league_id, is_active);

-- ============================
-- USEFUL VIEW
-- ============================

CREATE VIEW league_roster_rules AS
SELECT 
    l.league_id,
    l.league_name,
    rc.configuration_name,
    rc.active_roster_size,
    rc.injured_reserve_size,
    rc.practice_squad_size,
    
    -- Position requirements summary
    (rc.min_qb + rc.min_rb + rc.min_fb + rc.min_wr + rc.min_te + 
     rc.min_ol + rc.min_dl + rc.min_lb + rc.min_db + rc.min_k + rc.min_p) as total_min_positions,
    
    rc.allow_position_changes,
    rc.require_depth_chart,
    rc.enforce_jersey_by_position,
    rc.enable_salary_cap,
    rc.salary_cap_amount
    
FROM leagues l
JOIN roster_configuration rc ON l.league_id = rc.league_id
WHERE l.is_active = TRUE AND rc.is_active = TRUE;
