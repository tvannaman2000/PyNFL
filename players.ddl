-- Fixed Players table - removes subquery from generated column
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    
    -- Identity
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    display_name VARCHAR(50) GENERATED ALWAYS AS (
        first_name || ' ' || last_name 
    ) STORED,
    position_id INTEGER NOT NULL,
    position VARCHAR(5) NOT NULL,
    
    -- Physical characteristics
    height_inches INTEGER NOT NULL DEFAULT 72,
    height_display VARCHAR(10) GENERATED ALWAYS AS (
        (height_inches / 12) || ''' ' || (height_inches % 12) || '"'
    ) STORED,
    weight INTEGER NOT NULL DEFAULT 200,
    age INTEGER, -- Current age, can be updated
    
    -- Performance metrics
    years_experience INTEGER NOT NULL DEFAULT 0,
    speed_40_time DECIMAL(3,2),
    
    -- NFL Challenge skill ratings (50-99 scale)
    skill_run INTEGER NOT NULL DEFAULT 50 CHECK (skill_run >= 50 AND skill_run <= 99),
    skill_pass INTEGER NOT NULL DEFAULT 50 CHECK (skill_pass >= 50 AND skill_pass <= 99),
    skill_receive INTEGER NOT NULL DEFAULT 50 CHECK (skill_receive >= 50 AND skill_receive <= 99),
    skill_block INTEGER NOT NULL DEFAULT 50 CHECK (skill_block >= 50 AND skill_block <= 99),
    skill_kick INTEGER NOT NULL DEFAULT 50 CHECK (skill_kick >= 50 AND skill_kick <= 99),
    
    -- Overall rating (calculated by triggers, not generated)
    overall_rating INTEGER DEFAULT 50,
    
    -- Career management
    draft_year INTEGER,
    draft_round INTEGER,
    draft_pick INTEGER,
    created_season INTEGER NOT NULL,
    retired_season INTEGER,
    
    -- Status flags
    player_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (player_status IN ('ACTIVE', 'RETIRED', 'INJURED_RESERVE', 'SUSPENDED')),
    
    -- Development tracking
    skill_development_points INTEGER DEFAULT 0,
    last_skill_update_season INTEGER,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (height_inches >= 60 AND height_inches <= 84),
    CHECK (weight >= 120 AND weight <= 400),
    CHECK (years_experience >= 0 AND years_experience <= 25),
    CHECK (speed_40_time IS NULL OR (speed_40_time >= 4.0 AND speed_40_time <= 6.0)),
    CHECK (age IS NULL OR (age >= 18 AND age <= 50))
);

-- ============================
-- TRIGGERS TO AUTO-CALCULATE OVERALL RATING
-- ============================

-- Function to calculate overall rating
-- (SQLite doesn't have user-defined functions, so we'll embed this in triggers)

-- Trigger for INSERT - calculate initial overall rating
CREATE TRIGGER calculate_overall_rating_insert
AFTER INSERT ON players
FOR EACH ROW
BEGIN
    UPDATE players 
    SET overall_rating = CAST((
        NEW.skill_run * pos.weight_run + 
        NEW.skill_pass * pos.weight_pass + 
        NEW.skill_receive * pos.weight_receive + 
        NEW.skill_block * pos.weight_block + 
        NEW.skill_kick * pos.weight_kick + 
        (100 - COALESCE(NEW.speed_40_time * 10, 45)) * pos.weight_speed
    ) AS INTEGER)
    FROM positions pos 
    WHERE pos.position_id = NEW.position_id
      AND players.player_id = NEW.player_id;
END;

-- Trigger for UPDATE - recalculate when skills or position change
CREATE TRIGGER calculate_overall_rating_update
AFTER UPDATE OF skill_run, skill_pass, skill_receive, skill_block, skill_kick, speed_40_time, position_id ON players
FOR EACH ROW
BEGIN
    UPDATE players 
    SET overall_rating = CAST((
        NEW.skill_run * pos.weight_run + 
        NEW.skill_pass * pos.weight_pass + 
        NEW.skill_receive * pos.weight_receive + 
        NEW.skill_block * pos.weight_block + 
        NEW.skill_kick * pos.weight_kick + 
        (100 - COALESCE(NEW.speed_40_time * 10, 45)) * pos.weight_speed
    ) AS INTEGER),
    last_modified = CURRENT_TIMESTAMP
    FROM positions pos 
    WHERE pos.position_id = NEW.position_id
      AND players.player_id = NEW.player_id;
END;

-- Trigger to update position VARCHAR when position_id changes
CREATE TRIGGER sync_player_position_on_update
AFTER UPDATE OF position_id ON players
FOR EACH ROW
BEGIN
    UPDATE players 
    SET position = (SELECT position_code FROM positions WHERE position_id = NEW.position_id)
    WHERE player_id = NEW.player_id;
END;

-- ============================
-- HELPER FUNCTION (as a view for easy access)
-- ============================

-- View to show players with position details and calculated ratings
CREATE VIEW players_with_ratings AS
SELECT 
    p.*,
    pos.position_name,
    pos.position_group,
    pos.unit_type,
    -- Show the rating calculation breakdown
    ROUND(p.skill_run * pos.weight_run, 1) as run_contribution,
    ROUND(p.skill_pass * pos.weight_pass, 1) as pass_contribution,
    ROUND(p.skill_receive * pos.weight_receive, 1) as receive_contribution,
    ROUND(p.skill_block * pos.weight_block, 1) as block_contribution,
    ROUND(p.skill_kick * pos.weight_kick, 1) as kick_contribution,
    ROUND((100 - COALESCE(p.speed_40_time * 10, 45)) * pos.weight_speed, 1) as speed_contribution
FROM players p
JOIN positions pos ON p.position_id = pos.position_id
WHERE p.player_status = 'ACTIVE';

-- ============================
-- MANUAL RATING CALCULATION FUNCTION (for testing/debugging)
-- ============================

-- Since SQLite doesn't have user-defined functions, here's the SQL to manually recalculate all ratings:
/*
UPDATE players 
SET overall_rating = CAST((
    skill_run * pos.weight_run + 
    skill_pass * pos.weight_pass + 
    skill_receive * pos.weight_receive + 
    skill_block * pos.weight_block + 
    skill_kick * pos.weight_kick + 
    (100 - COALESCE(speed_40_time * 10, 45)) * pos.weight_speed
) AS INTEGER)
FROM positions pos 
WHERE pos.position_id = players.position_id;
*/
