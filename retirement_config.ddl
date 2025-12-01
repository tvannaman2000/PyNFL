-- retirement_config.ddl
-- Database schema for player retirement configuration
-- Version: 1.1
-- Date: 2025-12-01

-- ============================================================================
-- Position Retirement Configuration - ADD TO EXISTING POSITIONS TABLE
-- ============================================================================
-- These columns should be added to the existing positions table to store
-- retirement settings for each position
-- ============================================================================

-- Add retirement configuration columns to positions table
ALTER TABLE positions ADD COLUMN min_career_years INTEGER DEFAULT 4;
ALTER TABLE positions ADD COLUMN force_retire_age INTEGER DEFAULT 45;
ALTER TABLE positions ADD COLUMN base_retirement_age INTEGER DEFAULT 27;
ALTER TABLE positions ADD COLUMN base_retirement_probability DECIMAL(5,2) DEFAULT 5.0;
ALTER TABLE positions ADD COLUMN skill_retirement_weight DECIMAL(5,2) DEFAULT 0.3;

-- ============================================================================
-- Retirement Age Weight Multipliers
-- ============================================================================
-- Stores age-specific multipliers applied to base retirement probability
-- Allows different retirement curves per position
-- Final probability = base_retirement_probability * age_multiplier * skill_factor
-- ============================================================================

CREATE TABLE IF NOT EXISTS retirement_age_weights (
    position VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    age_multiplier DECIMAL(5,3) DEFAULT 1.0 NOT NULL,
    PRIMARY KEY (position, age),
    FOREIGN KEY (position) REFERENCES positions(position_code)
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_retirement_age_weights_position
    ON retirement_age_weights(position);

CREATE INDEX IF NOT EXISTS idx_retirement_age_weights_age
    ON retirement_age_weights(age);

-- ============================================================================
-- Sample Data - Running Back (RB)
-- Short career position - early retirement curve
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 38,
--     base_retirement_age = 27,
--     base_retirement_probability = 5.0,
--     skill_retirement_weight = 0.3
-- WHERE position_code = 'RB';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('RB', 27, 1.0),
-- ('RB', 28, 1.5),
-- ('RB', 29, 2.0),
-- ('RB', 30, 3.0),
-- ('RB', 31, 4.5),
-- ('RB', 32, 6.0),
-- ('RB', 33, 8.0),
-- ('RB', 34, 10.0),
-- ('RB', 35, 12.0),
-- ('RB', 36, 15.0),
-- ('RB', 37, 18.0);

-- ============================================================================
-- Sample Data - Quarterback (QB)
-- Long career position - delayed retirement curve
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 45,
--     base_retirement_age = 32,
--     base_retirement_probability = 3.0,
--     skill_retirement_weight = 0.4
-- WHERE position_code = 'QB';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('QB', 32, 1.0),
-- ('QB', 33, 1.2),
-- ('QB', 34, 1.5),
-- ('QB', 35, 2.0),
-- ('QB', 36, 2.5),
-- ('QB', 37, 3.5),
-- ('QB', 38, 5.0),
-- ('QB', 39, 7.0),
-- ('QB', 40, 10.0),
-- ('QB', 41, 13.0),
-- ('QB', 42, 16.0),
-- ('QB', 43, 20.0),
-- ('QB', 44, 25.0);

-- ============================================================================
-- Sample Data - Kicker (K)
-- Very long career position - minimal retirement curve
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 48,
--     base_retirement_age = 35,
--     base_retirement_probability = 2.0,
--     skill_retirement_weight = 0.2
-- WHERE position_code = 'K';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('K', 35, 1.0),
-- ('K', 36, 1.1),
-- ('K', 37, 1.3),
-- ('K', 38, 1.5),
-- ('K', 39, 1.8),
-- ('K', 40, 2.2),
-- ('K', 41, 2.7),
-- ('K', 42, 3.5),
-- ('K', 43, 4.5),
-- ('K', 44, 6.0),
-- ('K', 45, 8.0),
-- ('K', 46, 11.0),
-- ('K', 47, 15.0);

-- ============================================================================
-- Sample Data - Punter (P)
-- Very long career position - minimal retirement curve (similar to K)
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 48,
--     base_retirement_age = 35,
--     base_retirement_probability = 2.0,
--     skill_retirement_weight = 0.2
-- WHERE position_code = 'P';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('P', 35, 1.0),
-- ('P', 36, 1.1),
-- ('P', 37, 1.3),
-- ('P', 38, 1.5),
-- ('P', 39, 1.8),
-- ('P', 40, 2.2),
-- ('P', 41, 2.7),
-- ('P', 42, 3.5),
-- ('P', 43, 4.5),
-- ('P', 44, 6.0),
-- ('P', 45, 8.0),
-- ('P', 46, 11.0),
-- ('P', 47, 15.0);

-- ============================================================================
-- Sample Data - Wide Receiver (WR)
-- Medium-short career - speed/athleticism dependent
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 40,
--     base_retirement_age = 29,
--     base_retirement_probability = 4.0,
--     skill_retirement_weight = 0.35
-- WHERE position_code = 'WR';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('WR', 29, 1.0),
-- ('WR', 30, 1.5),
-- ('WR', 31, 2.0),
-- ('WR', 32, 2.8),
-- ('WR', 33, 4.0),
-- ('WR', 34, 5.5),
-- ('WR', 35, 7.5),
-- ('WR', 36, 10.0),
-- ('WR', 37, 13.0),
-- ('WR', 38, 16.0),
-- ('WR', 39, 20.0);

-- ============================================================================
-- Sample Data - Center (C)
-- Medium-long career - offensive line position
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 40,
--     base_retirement_age = 30,
--     base_retirement_probability = 4.0,
--     skill_retirement_weight = 0.25
-- WHERE position_code = 'C';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('C', 30, 1.0),
-- ('C', 31, 1.3),
-- ('C', 32, 1.7),
-- ('C', 33, 2.2),
-- ('C', 34, 3.0),
-- ('C', 35, 4.0),
-- ('C', 36, 5.5),
-- ('C', 37, 7.5),
-- ('C', 38, 10.0),
-- ('C', 39, 14.0);

-- ============================================================================
-- Sample Data - Offensive Line (OL)
-- Medium-long career - similar to center
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 40,
--     base_retirement_age = 30,
--     base_retirement_probability = 4.0,
--     skill_retirement_weight = 0.25
-- WHERE position_code = 'OL';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('OL', 30, 1.0),
-- ('OL', 31, 1.3),
-- ('OL', 32, 1.7),
-- ('OL', 33, 2.2),
-- ('OL', 34, 3.0),
-- ('OL', 35, 4.0),
-- ('OL', 36, 5.5),
-- ('OL', 37, 7.5),
-- ('OL', 38, 10.0),
-- ('OL', 39, 14.0);

-- ============================================================================
-- Sample Data - Defensive Line (DL)
-- Medium career - physical position
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 38,
--     base_retirement_age = 28,
--     base_retirement_probability = 4.5,
--     skill_retirement_weight = 0.3
-- WHERE position_code = 'DL';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('DL', 28, 1.0),
-- ('DL', 29, 1.5),
-- ('DL', 30, 2.2),
-- ('DL', 31, 3.0),
-- ('DL', 32, 4.5),
-- ('DL', 33, 6.5),
-- ('DL', 34, 9.0),
-- ('DL', 35, 12.0),
-- ('DL', 36, 15.0),
-- ('DL', 37, 18.0);

-- ============================================================================
-- Sample Data - Linebacker (LB)
-- Medium career - speed and physicality
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 38,
--     base_retirement_age = 28,
--     base_retirement_probability = 4.5,
--     skill_retirement_weight = 0.3
-- WHERE position_code = 'LB';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('LB', 28, 1.0),
-- ('LB', 29, 1.5),
-- ('LB', 30, 2.2),
-- ('LB', 31, 3.0),
-- ('LB', 32, 4.5),
-- ('LB', 33, 6.5),
-- ('LB', 34, 9.0),
-- ('LB', 35, 12.0),
-- ('LB', 36, 15.0),
-- ('LB', 37, 18.0);

-- ============================================================================
-- Sample Data - Defensive Back (DB)
-- Medium career - speed dependent
-- ============================================================================

-- UPDATE positions SET
--     min_career_years = 4,
--     force_retire_age = 38,
--     base_retirement_age = 28,
--     base_retirement_probability = 4.5,
--     skill_retirement_weight = 0.35
-- WHERE position_code = 'DB';

-- INSERT INTO retirement_age_weights (position, age, age_multiplier) VALUES
-- ('DB', 28, 1.0),
-- ('DB', 29, 1.5),
-- ('DB', 30, 2.2),
-- ('DB', 31, 3.2),
-- ('DB', 32, 4.5),
-- ('DB', 33, 6.5),
-- ('DB', 34, 9.0),
-- ('DB', 35, 12.0),
-- ('DB', 36, 15.0),
-- ('DB', 37, 18.0);

-- ============================================================================
-- Notes:
-- ============================================================================
-- 1. base_retirement_probability: Starting retirement chance % at base_retirement_age
-- 2. age_multiplier: Multiplier applied to base probability for each age
-- 3. skill_retirement_weight: Factor (0-1) determining how much skill decline
--    affects retirement probability
-- 4. min_career_years: Players won't retire before completing this many seasons
-- 5. force_retire_age: Players automatically retire at this age
-- 6. Final retirement probability calculation:
--    final_prob = base_retirement_probability * age_multiplier *
--                 (1 + skill_decline * skill_retirement_weight)
-- ============================================================================
