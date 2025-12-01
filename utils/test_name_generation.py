# v1.0
# src/utils/qb_rookie_generator.py
"""
QB Rookie Generation Script
Generates QB rookies based on player_generation_config table settings.
Uses positions table for physical characteristics and name tables for weighted names.
"""

import sqlite3
import random


def get_connection(db_path):
    """Get database connection with Row factory"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def check_existing_rookies(db_path, league_id, draft_year):
    """Check if rookies already exist for this league and draft year"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM rookies 
            WHERE league_id = ? AND draft_year = ?
        """, (league_id, draft_year))
        
        count = cursor.fetchone()['count']
        return count > 0


def get_league_info(db_path, league_id):
    """Get current league season information"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT current_season 
            FROM leagues 
            WHERE league_id = ?
        """, (league_id,))
        
        result = cursor.fetchone()
        if result:
            return result['current_season']
        return None


def load_name_data(db_path):
    """Load first and last names with their weights"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Load first names with weights (invert ranks: 1=most common becomes highest weight)
        cursor.execute("SELECT first_name, rank FROM first_names")
        first_data = cursor.fetchall()
        first_names = [row[0] for row in first_data]
        max_first_rank = max(row[1] for row in first_data)
        first_weights = [max_first_rank - row[1] + 1 for row in first_data]
        
        # Load last names with weights (invert ranks: 1=most common becomes highest weight)
        cursor.execute("SELECT last_name, last_name_rank FROM last_names")
        last_data = cursor.fetchall()
        last_names = [row[0] for row in last_data]
        max_last_rank = max(row[1] for row in last_data)
        last_weights = [max_last_rank - row[1] + 1 for row in last_data]
        
        return (first_names, first_weights, last_names, last_weights)


def get_qb_generation_config(db_path):
    """Get QB generation configuration"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM player_generation_config 
            WHERE position = 'QB'
        """)
        
        config = cursor.fetchone()
        if not config:
            raise ValueError("No configuration found for QB position")
        
        return dict(config)


def get_qb_data(db_path):
    """Get QB physical characteristics and rating weights from positions table"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT typical_height_min, typical_height_max,
                   typical_weight_min, typical_weight_max,
                   weight_run, weight_pass, weight_receive, 
                   weight_block, weight_kick, weight_speed
            FROM positions 
            WHERE position_code = 'QB'
        """)
        
        result = cursor.fetchone()
        if not result:
            raise ValueError("No position data found for QB")
        
        return dict(result)


def generate_qb_name(first_names, first_weights, last_names, last_weights):
    """Generate a random QB name using weighted selection"""
    first = random.choices(first_names, weights=first_weights, k=1)[0]
    last = random.choices(last_names, weights=last_weights, k=1)[0]
    
    # Capitalize properly (first letter only)
    first = first[0].upper() + first[1:].lower() if len(first) > 0 else first
    last = last[0].upper() + last[1:].lower() if len(last) > 0 else last
    
    return first, last


def calculate_qb_rating(skills, speed_40_time, weights):
    """Calculate position-specific overall rating using weights from positions table"""
    # Convert 40-yard dash time to speed rating (lower time = higher rating)
    speed_rating = 100 - (speed_40_time * 10)
    if speed_rating < 50:
        speed_rating = 50  # Floor at 50
    if speed_rating > 99:
        speed_rating = 99  # Ceiling at 99
    
    # Calculate weighted overall rating
    overall = (skills['skill_run'] * weights['weight_run'] + 
               skills['skill_pass'] * weights['weight_pass'] + 
               skills['skill_receive'] * weights['weight_receive'] + 
               skills['skill_block'] * weights['weight_block'] + 
               skills['skill_kick'] * weights['weight_kick'] +
               speed_rating * weights['weight_speed'])
    
    return round(overall)


def generate_qb_physical_stats(qb_data):
    """Generate height, weight, age, and speed for QB"""
    height = random.randint(qb_data['typical_height_min'], 
                           qb_data['typical_height_max'])
    weight = random.randint(qb_data['typical_weight_min'], 
                           qb_data['typical_weight_max'])
    age = random.randint(21, 23)  # Rookie age range
    
    # QB speed range: 4.5 - 5.1 seconds (40-yard dash)
    speed = round(random.uniform(4.5, 5.1), 2)
    
    return height, weight, age, speed


def generate_qb_skills(skill_min, skill_max):
    """Generate skill ratings for QB within the specified range"""
    # QBs only get randomized skills for their primary disciplines
    # All other skills default to 50
    return {
        'skill_run': random.randint(skill_min, skill_max),    # QBs need mobility
        'skill_pass': random.randint(skill_min, skill_max),   # Primary QB skill
        'skill_receive': 50,                                  # Not a QB discipline
        'skill_block': 50,                                    # Not a QB discipline  
        'skill_kick': 50                                      # Not a QB discipline
    }


def create_rookies_table_if_not_exists(db_path):
    """Create rookies table if it doesn't exist"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rookies (
                rookie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                draft_year INTEGER NOT NULL,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                position VARCHAR(5) NOT NULL,
                height_inches INTEGER NOT NULL,
                weight INTEGER NOT NULL,
                age INTEGER NOT NULL,
                speed_40_time DECIMAL(3,2),
                skill_run INTEGER NOT NULL,
                skill_pass INTEGER NOT NULL,
                skill_receive INTEGER NOT NULL,
                skill_block INTEGER NOT NULL,
                skill_kick INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                pos_rank INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (league_id) REFERENCES leagues(league_id)
            )
        """)
        
        conn.commit()


def insert_rookie_qb(db_path, league_id, draft_year, first_name, last_name, 
                    height, weight, age, speed, skills, rating):
    """Insert a rookie QB into the database"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rookies (
                league_id, draft_year, first_name, last_name, position,
                height_inches, weight, age, speed_40_time,
                skill_run, skill_pass, skill_receive, skill_block, skill_kick, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            league_id, draft_year, first_name, last_name, 'QB',
            height, weight, age, speed,
            skills['skill_run'], skills['skill_pass'], skills['skill_receive'],
            skills['skill_block'], skills['skill_kick'], rating
        ))
        
        conn.commit()
        return cursor.lastrowid


def update_qb_rankings(db_path, league_id, draft_year):
    """Update pos_rank for all QBs based on their rating"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all QBs ordered by rating (highest first)
        cursor.execute("""
            SELECT rookie_id, rating
            FROM rookies 
            WHERE league_id = ? AND draft_year = ? AND position = 'QB'
            ORDER BY rating DESC
        """, (league_id, draft_year))
        
        qbs = cursor.fetchall()
        
        # Update pos_rank (1 = best, 2 = second best, etc.)
        for rank, qb in enumerate(qbs, 1):
            cursor.execute("""
                UPDATE rookies 
                SET pos_rank = ? 
                WHERE rookie_id = ?
            """, (rank, qb['rookie_id']))
        
        conn.commit()
        print(f"Updated rankings for {len(qbs)} QBs")


def get_rb_generation_config(db_path):
    """Get RB generation configuration"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM player_generation_config 
            WHERE position = 'RB'
        """)
        
        config = cursor.fetchone()
        if not config:
            raise ValueError("No configuration found for RB position")
        
        return dict(config)


def get_rb_data(db_path):
    """Get RB physical characteristics and rating weights from positions table"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT typical_height_min, typical_height_max,
                   typical_weight_min, typical_weight_max,
                   weight_run, weight_pass, weight_receive, 
                   weight_block, weight_kick, weight_speed
            FROM positions 
            WHERE position_code = 'RB'
        """)
        
        result = cursor.fetchone()
        if not result:
            raise ValueError("No position data found for RB")
        
        return dict(result)


def generate_rb_name(first_names, first_weights, last_names, last_weights):
    """Generate a random RB name using weighted selection"""
    first = random.choices(first_names, weights=first_weights, k=1)[0]
    last = random.choices(last_names, weights=last_weights, k=1)[0]
    
    # Capitalize properly (first letter only)
    first = first[0].upper() + first[1:].lower() if len(first) > 0 else first
    last = last[0].upper() + last[1:].lower() if len(last) > 0 else last
    
    return first, last


def calculate_rb_rating(skills, speed_40_time, weights):
    """Calculate position-specific overall rating using weights from positions table"""
    # Convert 40-yard dash time to speed rating (lower time = higher rating)
    speed_rating = 100 - (speed_40_time * 10)
    if speed_rating < 50:
        speed_rating = 50  # Floor at 50
    if speed_rating > 99:
        speed_rating = 99  # Ceiling at 99
    
    # Calculate weighted overall rating
    overall = (skills['skill_run'] * weights['weight_run'] + 
               skills['skill_pass'] * weights['weight_pass'] + 
               skills['skill_receive'] * weights['weight_receive'] + 
               skills['skill_block'] * weights['weight_block'] + 
               skills['skill_kick'] * weights['weight_kick'] +
               speed_rating * weights['weight_speed'])
    
    return round(overall)


def generate_rb_physical_stats(rb_data):
    """Generate height, weight, age, and speed for RB"""
    height = random.randint(rb_data['typical_height_min'], 
                           rb_data['typical_height_max'])
    weight = random.randint(rb_data['typical_weight_min'], 
                           rb_data['typical_weight_max'])
    age = random.randint(21, 23)  # Rookie age range
    
    # RB speed range: 4.3 - 4.8 seconds (40-yard dash) - faster than QBs
    speed = round(random.uniform(4.3, 4.8), 2)
    
    return height, weight, age, speed


def generate_rb_skills(skill_min, skill_max):
    """Generate skill ratings for RB within the specified range"""
    # RBs get randomized skills for their primary disciplines
    # Pass and kick default to 50
    return {
        'skill_run': random.randint(skill_min, skill_max),      # Primary RB skill
        'skill_pass': 50,                                       # Not an RB discipline
        'skill_receive': random.randint(skill_min, skill_max),  # RBs catch passes
        'skill_block': random.randint(skill_min, skill_max),    # RBs block for protection
        'skill_kick': 50                                        # Not an RB discipline
    }


def insert_rookie_rb(db_path, league_id, draft_year, first_name, last_name, 
                    height, weight, age, speed, skills, rating):
    """Insert a rookie RB into the database"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rookies (
                league_id, draft_year, first_name, last_name, position,
                height_inches, weight, age, speed_40_time,
                skill_run, skill_pass, skill_receive, skill_block, skill_kick, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            league_id, draft_year, first_name, last_name, 'RB',
            height, weight, age, speed,
            skills['skill_run'], skills['skill_pass'], skills['skill_receive'],
            skills['skill_block'], skills['skill_kick'], rating
        ))
        
        conn.commit()
        return cursor.lastrowid


def update_rb_rankings(db_path, league_id, draft_year):
    """Update pos_rank for all RBs based on their rating"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all RBs ordered by rating (highest first)
        cursor.execute("""
            SELECT rookie_id, rating
            FROM rookies 
            WHERE league_id = ? AND draft_year = ? AND position = 'RB'
            ORDER BY rating DESC
        """, (league_id, draft_year))
        
        rbs = cursor.fetchall()
        
        # Update pos_rank (1 = best, 2 = second best, etc.)
        for rank, rb in enumerate(rbs, 1):
            cursor.execute("""
                UPDATE rookies 
                SET pos_rank = ? 
                WHERE rookie_id = ?
            """, (rank, rb['rookie_id']))
        
        conn.commit()
        print(f"Updated rankings for {len(rbs)} RBs")


def generate_rb_rookies(db_path, league_id):
    """Main function to generate RB rookies"""
    print("=" * 60)
    print("RB ROOKIE GENERATION")
    print("=" * 60)
    
    # Get current season and calculate draft year
    current_season = get_league_info(db_path, league_id)
    if current_season is None:
        print(f"Error: Could not find league {league_id}")
        return False
    
    draft_year = current_season + 1
    print(f"League ID: {league_id}")
    print(f"Current Season: {current_season}")
    print(f"Draft Year: {draft_year}")
    
    # Check if rookies already exist
    if check_existing_rookies(db_path, league_id, draft_year):
        response = input(f"\nRookies already exist for draft year {draft_year}. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Generation cancelled.")
            return False
    
    # Ensure rookies table exists
    create_rookies_table_if_not_exists(db_path)
    
    # Load name data
    print("\nLoading name data...")
    first_names, first_weights, last_names, last_weights = load_name_data(db_path)
    print(f"Loaded {len(first_names)} first names and {len(last_names)} last names")
    
    # Get RB configuration and position data
    print("\nGetting RB generation configuration...")
    config = get_rb_generation_config(db_path)
    print(f"Blue chip: {config['blue_chip_min_qty']}-{config['blue_chip_max_qty']} players, skills {config['blue_chip_min_skill']}-{config['blue_chip_max_skill']}")
    print(f"Average: {config['average_min_qty']}-{config['average_max_qty']} players, skills {config['average_min_skill']}-{config['average_max_skill']}")
    print(f"Below average: {config['below_average_min_qty']}-{config['below_average_max_qty']} players, skills {config['below_average_min_skill']}-{config['below_average_max_skill']}")
    
    # Get RB physical ranges and rating weights
    print("\nGetting RB position data...")
    rb_data = get_rb_data(db_path)
    print(f"Height: {rb_data['typical_height_min']}-{rb_data['typical_height_max']} inches")
    print(f"Weight: {rb_data['typical_weight_min']}-{rb_data['typical_weight_max']} lbs")
    print(f"Rating weights: Run={rb_data['weight_run']}, Receive={rb_data['weight_receive']}, Block={rb_data['weight_block']}, Speed={rb_data['weight_speed']}")
    
    # Generate rookies for each tier
    total_generated = 0
    
    # Blue chip RBs
    blue_chip_count = random.randint(config['blue_chip_min_qty'], config['blue_chip_max_qty'])
    print(f"\nGenerating {blue_chip_count} blue chip RBs...")
    for i in range(blue_chip_count):
        first_name, last_name = generate_rb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_rb_physical_stats(rb_data)
        skills = generate_rb_skills(config['blue_chip_min_skill'], config['blue_chip_max_skill'])
        rating = calculate_rb_rating(skills, speed, rb_data)
        
        rookie_id = insert_rookie_rb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Average RBs
    average_count = random.randint(config['average_min_qty'], config['average_max_qty'])
    print(f"\nGenerating {average_count} average RBs...")
    for i in range(average_count):
        first_name, last_name = generate_rb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_rb_physical_stats(rb_data)
        skills = generate_rb_skills(config['average_min_skill'], config['average_max_skill'])
        rating = calculate_rb_rating(skills, speed, rb_data)
        
        rookie_id = insert_rookie_rb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Below average RBs
    below_avg_count = random.randint(config['below_average_min_qty'], config['below_average_max_qty'])
    print(f"\nGenerating {below_avg_count} below average RBs...")
    for i in range(below_avg_count):
        first_name, last_name = generate_rb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_rb_physical_stats(rb_data)
        skills = generate_rb_skills(config['below_average_min_skill'], config['below_average_max_skill'])
        rating = calculate_rb_rating(skills, speed, rb_data)
        
        rookie_id = insert_rookie_rb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Update rankings based on calculated ratings
    print(f"\nUpdating RB rankings...")
    update_rb_rankings(db_path, league_id, draft_year)
    
    print("\n" + "=" * 60)
    print(f"RB ROOKIE GENERATION COMPLETE")
    print(f"Total RBs generated: {total_generated}")
    print(f"Blue chip: {blue_chip_count}, Average: {average_count}, Below average: {below_avg_count}")
    print("=" * 60)
    
    return True


def generate_qb_rookies(db_path, league_id):
    """Main function to generate QB rookies"""
    print("=" * 60)
    print("QB ROOKIE GENERATION")
    print("=" * 60)
    
    # Get current season and calculate draft year
    current_season = get_league_info(db_path, league_id)
    if current_season is None:
        print(f"Error: Could not find league {league_id}")
        return False
    
    draft_year = current_season + 1
    print(f"League ID: {league_id}")
    print(f"Current Season: {current_season}")
    print(f"Draft Year: {draft_year}")
    
    # Check if rookies already exist
    if check_existing_rookies(db_path, league_id, draft_year):
        response = input(f"\nRookies already exist for draft year {draft_year}. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Generation cancelled.")
            return False
    
    # Ensure rookies table exists
    create_rookies_table_if_not_exists(db_path)
    
    # Load name data
    print("\nLoading name data...")
    first_names, first_weights, last_names, last_weights = load_name_data(db_path)
    print(f"Loaded {len(first_names)} first names and {len(last_names)} last names")
    
    # Get QB configuration and position data
    print("\nGetting QB generation configuration...")
    config = get_qb_generation_config(db_path)
    print(f"Blue chip: {config['blue_chip_min_qty']}-{config['blue_chip_max_qty']} players, skills {config['blue_chip_min_skill']}-{config['blue_chip_max_skill']}")
    print(f"Average: {config['average_min_qty']}-{config['average_max_qty']} players, skills {config['average_min_skill']}-{config['average_max_skill']}")
    print(f"Below average: {config['below_average_min_qty']}-{config['below_average_max_qty']} players, skills {config['below_average_min_skill']}-{config['below_average_max_skill']}")
    
    # Get QB physical ranges and rating weights
    print("\nGetting QB position data...")
    qb_data = get_qb_data(db_path)
    print(f"Height: {qb_data['typical_height_min']}-{qb_data['typical_height_max']} inches")
    print(f"Weight: {qb_data['typical_weight_min']}-{qb_data['typical_weight_max']} lbs")
    print(f"Rating weights: Run={qb_data['weight_run']}, Pass={qb_data['weight_pass']}, Speed={qb_data['weight_speed']}")
    
    # Generate rookies for each tier
    total_generated = 0
    
    # Blue chip QBs
    blue_chip_count = random.randint(config['blue_chip_min_qty'], config['blue_chip_max_qty'])
    print(f"\nGenerating {blue_chip_count} blue chip QBs...")
    for i in range(blue_chip_count):
        first_name, last_name = generate_qb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_qb_physical_stats(qb_data)
        skills = generate_qb_skills(config['blue_chip_min_skill'], config['blue_chip_max_skill'])
        rating = calculate_qb_rating(skills, speed, qb_data)
        
        rookie_id = insert_rookie_qb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Average QBs
    average_count = random.randint(config['average_min_qty'], config['average_max_qty'])
    print(f"\nGenerating {average_count} average QBs...")
    for i in range(average_count):
        first_name, last_name = generate_qb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_qb_physical_stats(qb_data)
        skills = generate_qb_skills(config['average_min_skill'], config['average_max_skill'])
        rating = calculate_qb_rating(skills, speed, qb_data)
        
        rookie_id = insert_rookie_qb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Below average QBs
    below_avg_count = random.randint(config['below_average_min_qty'], config['below_average_max_qty'])
    print(f"\nGenerating {below_avg_count} below average QBs...")
    for i in range(below_avg_count):
        first_name, last_name = generate_qb_name(first_names, first_weights, last_names, last_weights)
        height, weight, age, speed = generate_qb_physical_stats(qb_data)
        skills = generate_qb_skills(config['below_average_min_skill'], config['below_average_max_skill'])
        rating = calculate_qb_rating(skills, speed, qb_data)
        
        rookie_id = insert_rookie_qb(db_path, league_id, draft_year, first_name, last_name,
                                   height, weight, age, speed, skills, rating)
        
        print(f"  {i+1}. {first_name} {last_name} - {height//12}'{height%12}\" {weight}lbs, {age}yo, {speed}s 40-yard, Rating: {rating}")
        print(f"     Skills: Run={skills['skill_run']}, Pass={skills['skill_pass']}, Rec={skills['skill_receive']}, Block={skills['skill_block']}, Kick={skills['skill_kick']}")
        total_generated += 1
    
    # Update rankings based on calculated ratings
    print(f"\nUpdating QB rankings...")
    update_qb_rankings(db_path, league_id, draft_year)
    
    print("\n" + "=" * 60)
    print(f"QB ROOKIE GENERATION COMPLETE")
    print(f"Total QBs generated: {total_generated}")
    print(f"Blue chip: {blue_chip_count}, Average: {average_count}, Below average: {below_avg_count}")
    print("=" * 60)
    
    return True


def main():
    """Test/example usage"""
    db_path = "pynfl.db"
    league_id = 1  # Default league ID
    
    # Generate QBs
    success_qb = generate_qb_rookies(db_path, league_id)
    if success_qb:
        print("QB rookie generation completed successfully!")
    else:
        print("QB rookie generation failed!")
    
    # Generate RBs
    success_rb = generate_rb_rookies(db_path, league_id)
    if success_rb:
        print("RB rookie generation completed successfully!")
    else:
        print("RB rookie generation failed!")
    
    # Overall success
    if success_qb and success_rb:
        print("\nAll rookie generation completed successfully!")
    else:
        print("\nSome rookie generation failed!")


if __name__ == "__main__":
    main()
