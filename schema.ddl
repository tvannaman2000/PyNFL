--------------------------------
-- League Management
--------------------------------

CREATE TABLE leagues (
    league_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_name VARCHAR(50) NOT NULL,
    created_date DATE NOT NULL,
    current_season INTEGER NOT NULL DEFAULT 1,
    current_week INTEGER NOT NULL DEFAULT 1,
    game_files_path VARCHAR(255),
    last_sync_timestamp DATETIME,
    regular_season_games INTEGER,
    playoff_teams_per_conf INTEGER,
    division_games INTEGER,
    conference_games INTEGER,
    interconference_games INTEGER,
    playoff_weeks INTEGER,
    preseason_games INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);


CREATE TABLE IF NOT EXISTS conferences (
    conference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    conference_name VARCHAR(50) NOT NULL,
    abbreviation VARCHAR(10), -- AFC, NFC, etc.
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    UNIQUE(league_id, conference_name),
    UNIQUE(league_id, abbreviation)
);


CREATE TABLE IF NOT EXISTS divisions (
    division_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conference_id INTEGER NOT NULL,
    division_name VARCHAR(50) NOT NULL,
    abbreviation VARCHAR(10), -- North, South, East, West, etc.
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (conference_id) REFERENCES conferences(conference_id) ON DELETE CASCADE,
    UNIQUE(conference_id, division_name),
    UNIQUE(conference_id, abbreviation)
);


CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL, -- Denormalized for faster queries
    division_id INTEGER,  -- Foreign key to divisions table (NULL = unassigned)
    conference_id INTEGER, -- Denormalized for faster queries (NULL = unassigned)
    
    -- Team Identity
    team_name VARCHAR(50) NOT NULL,
    city VARCHAR(50),
    full_name VARCHAR(100) GENERATED ALWAYS AS (
        CASE 
            WHEN city IS NOT NULL AND city != '' THEN city || ' ' || team_name
            ELSE team_name
        END
    ) STORED,
    abbreviation VARCHAR(5), -- DAL, NYG, KC, etc.
    
    -- Team Colors and Branding
    primary_color VARCHAR(7), -- Hex color codes (#FF0000)
    secondary_color VARCHAR(7),
    logo_path VARCHAR(255),
    
    -- Team History and Status
    founded_year INTEGER, -- Real world year team was founded
    created_season INTEGER , -- Season when added to this league
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Roster Filename
    roster_filename varchar(20),
    
    -- Foreign Key Constraints
    FOREIGN KEY (league_id) REFERENCES leagues(league_id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES divisions(division_id) ON DELETE SET NULL,
    FOREIGN KEY (conference_id) REFERENCES conferences(conference_id) ON DELETE SET NULL,
    
    -- Unique Constraints
    UNIQUE(league_id, team_name), -- No duplicate team names in same league
    UNIQUE(league_id, city, team_name), -- No duplicate city + team name combos
    UNIQUE(league_id, abbreviation), -- No duplicate abbreviations in same league
    
    -- Check Constraints
    CHECK (team_name IS NOT NULL AND team_name != '')
);

