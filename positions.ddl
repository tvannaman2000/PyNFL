-- ============================
-- POSITIONS TABLE - Master list of all valid positions
-- ============================

CREATE TABLE positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_code VARCHAR(5) NOT NULL UNIQUE, -- QB, RB, DE, etc.
    position_name VARCHAR(30) NOT NULL, -- Quarterback, Running Back, etc.
    position_group VARCHAR(20) NOT NULL 
        CHECK (position_group IN ('OFFENSE', 'DEFENSE', 'SPECIAL_TEAMS', 'SPECIAL_POSITION')),
    
    -- Detailed categorization
    unit_type VARCHAR(20), -- SKILL, LINE, LINEBACKER, SECONDARY, etc.
    
    -- Rating formula weights (0.0 to 1.0, should sum to 1.0)
    weight_run DECIMAL(3,2) DEFAULT 0.00,
    weight_pass DECIMAL(3,2) DEFAULT 0.00,
    weight_receive DECIMAL(3,2) DEFAULT 0.00,
    weight_block DECIMAL(3,2) DEFAULT 0.00,
    weight_kick DECIMAL(3,2) DEFAULT 0.00,
    weight_speed DECIMAL(3,2) DEFAULT 0.00,
    
    -- Position characteristics
    jersey_min INTEGER, -- Typical jersey number range
    jersey_max INTEGER,
    typical_height_min INTEGER, -- Typical height range in inches
    typical_height_max INTEGER,
    typical_weight_min INTEGER, -- Typical weight range
    typical_weight_max INTEGER,
    
    -- Display and organization
    depth_chart_order INTEGER, -- Order within position group for depth charts
    is_starter_position BOOLEAN DEFAULT TRUE, -- Can this position be a starter?
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure weights don't exceed 100%
    CHECK (weight_run + weight_pass + weight_receive + weight_block + weight_kick + weight_speed <= 1.01),
    CHECK (weight_run >= 0 AND weight_pass >= 0 AND weight_receive >= 0 AND 
           weight_block >= 0 AND weight_kick >= 0 AND weight_speed >= 0)
);

-- ============================
-- INSERT ALL POSITIONS WITH RATING FORMULAS
-- ============================

INSERT INTO positions (
    position_code, position_name, position_group, unit_type,
    weight_run, weight_pass, weight_receive, weight_block, weight_kick, weight_speed,
    jersey_min, jersey_max, typical_height_min, typical_height_max, typical_weight_min, typical_weight_max,
    depth_chart_order, description
) VALUES
-- OFFENSIVE POSITIONS
('QB', 'Quarterback', 'OFFENSE', 'SKILL', 0.20, 0.40, 0.10, 0.10, 0.00, 0.20, 1, 19, 72, 78, 200, 240, 1, 'Field general, primary passer'),
('RB', 'Running Back', 'OFFENSE', 'SKILL', 0.40, 0.05, 0.20, 0.20, 0.00, 0.15, 20, 49, 68, 74, 180, 220, 2, 'Primary ball carrier'),
('FB', 'Fullback', 'OFFENSE', 'SKILL', 0.30, 0.00, 0.10, 0.40, 0.00, 0.20, 30, 49, 70, 76, 220, 260, 3, 'Lead blocker and short-yardage back'),
('WR', 'Wide Receiver', 'OFFENSE', 'SKILL', 0.10, 0.00, 0.50, 0.10, 0.00, 0.30, 10, 19, 68, 78, 170, 220, 4, 'Primary pass catcher'),
('WR3', 'Wide Receiver', 'OFFENSE', 'SKILL', 0.10, 0.00, 0.50, 0.10, 0.00, 0.30, 10, 19, 68, 78, 170, 220, 4, 'Primary pass catcher'),
('TE', 'Tight End', 'OFFENSE', 'SKILL', 0.10, 0.00, 0.30, 0.40, 0.00, 0.20, 80, 89, 74, 80, 230, 270, 5, 'Receiver and blocker hybrid'),
('TE2', 'Tight End', 'OFFENSE', 'SKILL', 0.10, 0.00, 0.30, 0.40, 0.00, 0.20, 80, 89, 74, 80, 230, 270, 5, 'Receiver and blocker hybrid'),
('TE3', 'Tight End', 'OFFENSE', 'SKILL', 0.10, 0.00, 0.30, 0.40, 0.00, 0.20, 80, 89, 74, 80, 230, 270, 5, 'Receiver and blocker hybrid'),

-- OFFENSIVE LINE
('C', 'Center', 'OFFENSE', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 50, 79, 72, 78, 280, 320, 6, 'Snaps ball, calls protections'),
('OL', 'Offensive Line', 'OFFENSE', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 50, 79, 74, 80, 290, 340, 7, 'Generic offensive lineman'),

-- DEFENSIVE LINE  
('DE', 'Defensive End', 'DEFENSE', 'LINE', 0.30, 0.00, 0.05, 0.40, 0.00, 0.25, 90, 99, 74, 80, 250, 290, 8, 'Edge pass rusher'),
('DT', 'Defensive Tackle', 'DEFENSE', 'LINE', 0.30, 0.00, 0.05, 0.50, 0.00, 0.15, 90, 99, 72, 78, 280, 320, 9, 'Interior pass rusher'),
('NT', 'Nose Tackle', 'DEFENSE', 'LINE', 0.25, 0.00, 0.05, 0.55, 0.00, 0.15, 90, 99, 72, 78, 300, 350, 10, 'Run-stopping specialist'),
('R/NT', 'Right/Nose Tackle', 'DEFENSE', 'LINE', 0.25, 0.00, 0.05, 0.55, 0.00, 0.15, 90, 99, 72, 78, 300, 350, 10, 'Run-stopping specialist'),
('DL', 'Defensive Line', 'DEFENSE', 'LINE', 0.30, 0.00, 0.10, 0.40, 0.00, 0.20, 90, 99, 72, 80, 260, 310, 11, 'Generic defensive lineman'),

-- LINEBACKERS
('OLB', 'Outside Linebacker', 'DEFENSE', 'LINEBACKER', 0.30, 0.00, 0.25, 0.30, 0.00, 0.15, 50, 59, 72, 78, 220, 250, 12, 'Edge rusher and coverage'),
('ILB', 'Inside Linebacker', 'DEFENSE', 'LINEBACKER', 0.40, 0.00, 0.20, 0.25, 0.00, 0.15, 50, 59, 70, 76, 230, 260, 13, 'Run stopper and coverage'),
('LB', 'Linebacker', 'DEFENSE', 'LINEBACKER', 0.35, 0.00, 0.25, 0.25, 0.00, 0.15, 50, 59, 70, 78, 220, 260, 14, 'Generic linebacker'),

-- DEFENSIVE BACKS
('CB', 'Cornerback', 'DEFENSE', 'SECONDARY', 0.20, 0.00, 0.50, 0.00, 0.00, 0.30, 20, 49, 68, 76, 170, 200, 15, 'Pure coverage specialist'),
('SS', 'Strong Safety', 'DEFENSE', 'SECONDARY', 0.30, 0.00, 0.35, 0.15, 0.00, 0.20, 20, 49, 70, 76, 190, 220, 16, 'Run support and coverage'),
('FS', 'Free Safety', 'DEFENSE', 'SECONDARY', 0.25, 0.00, 0.40, 0.05, 0.00, 0.30, 20, 49, 70, 76, 180, 210, 17, 'Deep coverage specialist'),
('DB', 'Defensive Back', 'DEFENSE', 'SECONDARY', 0.25, 0.00, 0.45, 0.05, 0.00, 0.25, 20, 49, 68, 76, 170, 220, 18, 'Generic defensive back'),

-- SPECIAL TEAMS
('K', 'Kicker', 'SPECIAL_TEAMS', 'KICKING', 0.10, 0.10, 0.00, 0.00, 0.80, 0.00, 1, 19, 68, 76, 170, 220, 19, 'Field goals and extra points'),
('P', 'Punter', 'SPECIAL_TEAMS', 'KICKING', 0.10, 0.20, 0.10, 0.00, 0.60, 0.00, 1, 19, 70, 78, 190, 230, 20, 'Punting specialist'),

-- SPECIAL ROSTER POSITIONS (for depth chart management)
('LT', 'Left Tackle', 'SPECIAL_POSITION', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 70, 79, 76, 80, 300, 340, 21, 'Blind side protector'),
('LG', 'Left Guard', 'SPECIAL_POSITION', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 60, 79, 74, 78, 300, 330, 22, 'Interior pass protector'),
('RG', 'Right Guard', 'SPECIAL_POSITION', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 60, 79, 74, 78, 300, 330, 23, 'Interior pass protector'),
('RT', 'Right Tackle', 'SPECIAL_POSITION', 'LINE', 0.20, 0.00, 0.00, 0.70, 0.00, 0.10, 70, 79, 76, 80, 300, 340, 24, 'Right side protector'),
('LE', 'Left End', 'SPECIAL_POSITION', 'LINE', 0.30, 0.00, 0.05, 0.40, 0.00, 0.25, 90, 99, 74, 80, 250, 290, 25, 'Left defensive end'),
('RE', 'Right End', 'SPECIAL_POSITION', 'LINE', 0.30, 0.00, 0.05, 0.40, 0.00, 0.25, 90, 99, 74, 80, 250, 290, 26, 'Right defensive end'),
('LDT', 'Left Defensive Tackle', 'SPECIAL_POSITION', 'LINE', 0.30, 0.00, 0.05, 0.50, 0.00, 0.15, 90, 99, 72, 78, 280, 320, 27, 'Left side interior rusher'),
('LOLB', 'Left Outside Linebacker', 'SPECIAL_POSITION', 'LINEBACKER', 0.30, 0.00, 0.25, 0.30, 0.00, 0.15, 50, 59, 72, 78, 220, 250, 28, 'Left side edge rusher'),
('LILB', 'Left Inside Linebacker', 'SPECIAL_POSITION', 'LINEBACKER', 0.40, 0.00, 0.20, 0.25, 0.00, 0.15, 50, 59, 70, 76, 230, 260, 29, 'Left side run stopper'),
('RMLB', 'Right Middle Linebacker', 'SPECIAL_POSITION', 'LINEBACKER', 0.40, 0.00, 0.20, 0.25, 0.00, 0.15, 50, 59, 70, 76, 230, 260, 30, 'Right middle coverage'),
('ROLB', 'Right Outside Linebacker', 'SPECIAL_POSITION', 'LINEBACKER', 0.30, 0.00, 0.25, 0.30, 0.00, 0.15, 50, 59, 72, 78, 220, 250, 31, 'Right side edge rusher'),
('LCB', 'Left Cornerback', 'SPECIAL_POSITION', 'SECONDARY', 0.20, 0.00, 0.50, 0.00, 0.00, 0.30, 20, 49, 68, 76, 170, 200, 32, 'Left side coverage'),
('5<9b>', 'Nickel Back', 'SPECIAL_POSITION', 'SECONDARY', 0.20, 0.00, 0.50, 0.00, 0.00, 0.30, 20, 49, 68, 76, 170, 200, 32, 'Left side coverage'),
('10<9b>', 'Dime Back', 'SPECIAL_POSITION', 'SECONDARY', 0.20, 0.00, 0.50, 0.00, 0.00, 0.30, 20, 49, 68, 76, 170, 200, 32, 'Left side coverage'),
('RCB', 'Right Cornerback', 'SPECIAL_POSITION', 'SECONDARY', 0.20, 0.00, 0.50, 0.00, 0.00, 0.30, 20, 49, 68, 76, 170, 200, 33, 'Right side coverage'),
('FL', 'Flanker', 'SPECIAL_POSITION', 'SKILL', 0.10, 0.00, 0.50, 0.10, 0.00, 0.30, 10, 19, 68, 78, 170, 220, 34, 'Wide receiver variant'),
('SE', 'Split End', 'SPECIAL_POSITION', 'SKILL', 0.10, 0.00, 0.50, 0.10, 0.00, 0.30, 10, 19, 68, 78, 170, 220, 35, 'Wide receiver variant'),
('HB', 'Halfback', 'SPECIAL_POSITION', 'SKILL', 0.40, 0.05, 0.20, 0.20, 0.00, 0.15, 20, 49, 68, 74, 180, 220, 36, 'Running back variant'),
('PR', 'Punt Returner', 'SPECIAL_POSITION', 'RETURN', 0.20, 0.00, 0.30, 0.00, 0.00, 0.50, 10, 49, 68, 76, 170, 210, 37, 'Punt return specialist'),
('KR', 'Kick Returner', 'SPECIAL_POSITION', 'RETURN', 0.25, 0.00, 0.25, 0.00, 0.00, 0.50, 10, 49, 68, 76, 170, 210, 38, 'Kickoff return specialist');

-- ============================
-- INDEXES
-- ============================

CREATE INDEX idx_positions_code ON positions(position_code);
CREATE INDEX idx_positions_group ON positions(position_group, unit_type);
CREATE INDEX idx_positions_active ON positions(is_active, position_group);
