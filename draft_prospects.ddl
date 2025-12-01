-- ============================
-- DRAFT PROSPECTS TABLE - Potential draftees
-- ============================

CREATE TABLE draft_prospects (
    prospect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    draft_year INTEGER NOT NULL, -- Year they're eligible
    
    -- Identity
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    display_name VARCHAR(50) GENERATED ALWAYS AS (
        first_name || ' ' || last_name
    ) STORED,
    position VARCHAR(5) NOT NULL, -- Denormalized for convenience
    position_id INTEGER NOT NULL, -- FK for data integrity
    
    -- Physical characteristics
    height_inches INTEGER NOT NULL DEFAULT 72,
    height_display VARCHAR(10) GENERATED ALWAYS AS (
        (height_inches / 12) || ''' ' || (height_inches % 12) || '"'
    ) STORED,
    weight INTEGER NOT NULL DEFAULT 200,
    age INTEGER,
    
    -- Performance metrics
    speed_40_time DECIMAL(3,2),
    college VARCHAR(50), -- Where they played
    
    -- Projected NFL Challenge skill ratings (with some uncertainty)
    skill_run INTEGER NOT NULL DEFAULT 50 CHECK (skill_run >= 40 AND skill_run <= 95),
    skill_pass INTEGER NOT NULL DEFAULT 50 CHECK (skill_pass >= 40 AND skill_pass <= 95),
    skill_receive INTEGER NOT NULL DEFAULT 50 CHECK (skill_receive >= 40 AND skill_receive <= 95),
    skill_block INTEGER NOT NULL DEFAULT 50 CHECK (skill_block >= 40 AND skill_block <= 95),
    skill_kick INTEGER NOT NULL DEFAULT 50 CHECK (skill_kick >= 40 AND skill_kick <= 95),
    
    -- Draft projection/scouting
    projected_overall INTEGER GENERATED ALWAYS AS (
        CAST((
            SELECT 
                (dp.skill_run * pos.weight_run + 
                 dp.skill_pass * pos.weight_pass + 
                 dp.skill_receive * pos.weight_receive + 
                 dp.skill_block * pos.weight_block + 
                 dp.skill_kick * pos.weight_kick + 
                 (100 - COALESCE(dp.speed_40_time * 10, 45)) * pos.weight_speed)
            FROM positions pos 
            WHERE pos.position_id = dp.position_id
        ) AS INTEGER)
    ) STORED,
    
    projected_round INTEGER, -- Scout's projection: which round they might go
    draft_grade VARCHAR(10), -- A+, A, B+, B, C+, C, D, F
    
    -- Scouting notes
    strengths TEXT,
    weaknesses TEXT,
    scouting_notes TEXT,
    
    -- Status (no team association until drafted and signed)
    prospect_status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE'
        CHECK (prospect_status IN ('AVAILABLE', 'DRAFTED', 'UNDRAFTED_FA', 'INELIGIBLE')),
    draft_round INTEGER, -- Actual round drafted (NULL if undrafted)
    draft_pick INTEGER, -- Actual pick number (NULL if undrafted)
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id),
    
    -- Constraints
    CHECK (height_inches >= 60 AND height_inches <= 84),
    CHECK (weight >= 150 AND weight <= 400),
    CHECK (speed_40_time IS NULL OR (speed_40_time >= 4.0 AND speed_40_time <= 6.0)),
    CHECK (age IS NULL OR (age >= 18 AND age <= 30)),
    CHECK (projected_round IS NULL OR (projected_round >= 1 AND projected_round <= 7)),
    CHECK (draft_round IS NULL OR (draft_round >= 1 AND draft_round <= 7)),
    CHECK (draft_pick IS NULL OR draft_pick > 0)
);

-- ============================
-- SYNC TRIGGER - Keep position and position_id consistent
-- ============================

CREATE TRIGGER sync_prospect_position_on_insert
AFTER INSERT ON draft_prospects
FOR EACH ROW
BEGIN
    UPDATE draft_prospects 
    SET position = (SELECT position_code FROM positions WHERE position_id = NEW.position_id)
    WHERE prospect_id = NEW.prospect_id;
END;

CREATE TRIGGER sync_prospect_position_on_update
AFTER UPDATE OF position_id ON draft_prospects
FOR EACH ROW
BEGIN
    UPDATE draft_prospects 
    SET position = (SELECT position_code FROM positions WHERE position_id = NEW.position_id)
    WHERE prospect_id = NEW.prospect_id;
END;

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================

CREATE INDEX idx_prospects_league_year ON draft_prospects(league_id, draft_year);
CREATE INDEX idx_prospects_position ON draft_prospects(position, projected_overall DESC);
CREATE INDEX idx_prospects_position_id ON draft_prospects(position_id, projected_overall DESC);
CREATE INDEX idx_prospects_status ON draft_prospects(prospect_status, draft_year);
CREATE INDEX idx_prospects_grade ON draft_prospects(draft_grade, position);
CREATE INDEX idx_prospects_draft_order ON draft_prospects(draft_year, draft_round, draft_pick);
