# Version: 2.0
# File: utils/standings_calculator.py

"""
Standings Calculator Module

Calculates team standings with NFL-style tie-breaker rules:

FOR DIVISION STANDINGS (teams in same division):
1. Win percentage (primary)
2. Head-to-head record (within division)
3. Division record
4. Conference record
5. Points differential
6. Points scored

FOR WILD CARD SEEDING (teams from different divisions):
1. Win percentage (primary)
2. Conference record (NOT head-to-head)
3. Points differential
4. Points scored
"""

import sqlite3

def calculate_division_leaders(league_id, season, db_manager):
    """
    Calculate division standings with tie-breaker rules.
    
    This is for DIVISION STANDINGS display only.
    For playoff picture, use calculate_conference_playoff_seeds().
    
    Args:
        league_id: The league ID
        season: The season year
        db_manager: Database manager object (PyQt5 style)
        
    Returns:
        List of dictionaries with team standings sorted by division and tie-breakers
    """
    # Get connection from db_manager (same as dashboard_tab.py does)
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get all teams with their basic records
        query = """
            SELECT 
                t.team_id,
                t.full_name as team_name,
                t.abbreviation,
                t.division_id,
                d.division_name,
                d.conference_id,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id AND g.home_score > g.away_score) 
                      OR (g.away_team_id = t.team_id AND g.away_score > g.home_score) 
                    THEN 1 ELSE 0 END), 0) as wins,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id AND g.home_score < g.away_score) 
                      OR (g.away_team_id = t.team_id AND g.away_score < g.home_score) 
                    THEN 1 ELSE 0 END), 0) as losses,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id OR g.away_team_id = t.team_id) 
                     AND g.home_score = g.away_score 
                    THEN 1 ELSE 0 END), 0) as ties
            FROM teams t
            JOIN divisions d ON t.division_id = d.division_id
            LEFT JOIN games g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
                AND g.game_status = 'COMPLETED'
                AND g.season = ?
                AND g.league_id = ?
            WHERE t.league_id = ?
            GROUP BY t.team_id, t.full_name, t.abbreviation, t.division_id, d.division_name, d.conference_id
        """
        
        cursor.execute(query, (season, league_id, league_id))
        teams = cursor.fetchall()
        
        # Calculate additional tie-breaker stats for each team
        teams_with_tiebreakers = []
        for team in teams:
            team_id = team['team_id']
            
            # Get head-to-head, division, and conference records
            h2h_wins, h2h_losses = get_head_to_head_record(cursor, team_id, team['division_id'], season, league_id)
            div_wins, div_losses = get_division_record(cursor, team_id, team['division_id'], season, league_id)
            conf_wins, conf_losses = get_conference_record(cursor, team_id, team['conference_id'], season, league_id)
            points_diff = get_points_differential(cursor, team_id, season, league_id)
            points_for = get_points_scored(cursor, team_id, season, league_id)
            
            # Calculate win percentage
            total_games = team['wins'] + team['losses'] + team['ties']
            win_pct = team['wins'] / total_games if total_games > 0 else 0.0
            
            teams_with_tiebreakers.append({
                'team_id': team_id,
                'team_name': team['team_name'],
                'abbreviation': team['abbreviation'],
                'division_id': team['division_id'],
                'division_name': team['division_name'],
                'conference_id': team['conference_id'],
                'wins': team['wins'],
                'losses': team['losses'],
                'ties': team['ties'],
                'win_pct': win_pct,
                'h2h_wins': h2h_wins,
                'h2h_losses': h2h_losses,
                'div_wins': div_wins,
                'div_losses': div_losses,
                'conf_wins': conf_wins,
                'conf_losses': conf_losses,
                'points_diff': points_diff,
                'points_for': points_for
            })
        
        # Group by division and sort using tie-breaker rules
        divisions = {}
        for team in teams_with_tiebreakers:
            div_id = team['division_id']
            if div_id not in divisions:
                divisions[div_id] = []
            divisions[div_id].append(team)
        
        # Sort each division
        results = []
        for div_id, div_teams in divisions.items():
            sorted_teams = sort_teams_with_tiebreakers(div_teams)
            results.extend(sorted_teams)
        
        return results
        
    except Exception as e:
        print(f"Error in calculate_division_leaders: {e}")
        return []


def calculate_conference_playoff_seeds(league_id, season, conference_id, playoff_spots, db_manager):
    """
    Calculate playoff seeds for a conference with proper wild card tie-breaking.
    
    This should be used for PLAYOFF PICTURE display, not calculate_division_leaders.
    
    Key difference: Wild card candidates use CONFERENCE RECORD as the primary tie-breaker,
    not head-to-head within division.
    
    Args:
        league_id: The league ID
        season: The season year
        conference_id: The conference ID
        playoff_spots: Number of playoff teams
        db_manager: Database manager object
        
    Returns:
        List of teams in seed order with seed_number, seed_type, etc.
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get all teams in conference with their records
        query = """
            SELECT 
                t.team_id,
                t.full_name as team_name,
                t.abbreviation,
                t.division_id,
                d.division_name,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id AND g.home_score > g.away_score) 
                      OR (g.away_team_id = t.team_id AND g.away_score > g.home_score) 
                    THEN 1 ELSE 0 END), 0) as wins,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id AND g.home_score < g.away_score) 
                      OR (g.away_team_id = t.team_id AND g.away_score < g.home_score) 
                    THEN 1 ELSE 0 END), 0) as losses,
                COALESCE(SUM(CASE 
                    WHEN (g.home_team_id = t.team_id OR g.away_team_id = t.team_id) 
                     AND g.home_score = g.away_score 
                    THEN 1 ELSE 0 END), 0) as ties
            FROM teams t
            JOIN divisions d ON t.division_id = d.division_id
            LEFT JOIN games g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
                AND g.game_status = 'COMPLETED'
                AND g.season = ?
                AND g.league_id = ?
            WHERE d.conference_id = ? AND t.is_active = TRUE
            GROUP BY t.team_id, t.full_name, t.abbreviation, t.division_id, d.division_name
        """
        
        cursor.execute(query, (season, league_id, conference_id))
        teams = cursor.fetchall()
        
        # Calculate tie-breaker stats
        teams_with_stats = []
        for team in teams:
            team_id = team['team_id']
            
            div_wins, div_losses = get_division_record(cursor, team_id, team['division_id'], season, league_id)
            conf_wins, conf_losses = get_conference_record(cursor, team_id, conference_id, season, league_id)
            points_diff = get_points_differential(cursor, team_id, season, league_id)
            points_for = get_points_scored(cursor, team_id, season, league_id)
            
            total_games = team['wins'] + team['losses'] + team['ties']
            win_pct = team['wins'] / total_games if total_games > 0 else 0.0
            conf_pct = conf_wins / (conf_wins + conf_losses) if (conf_wins + conf_losses) > 0 else 0.0
            div_pct = div_wins / (div_wins + div_losses) if (div_wins + div_losses) > 0 else 0.0
            
            teams_with_stats.append({
                'team_id': team_id,
                'team_name': team['team_name'],
                'abbreviation': team['abbreviation'],
                'division_id': team['division_id'],
                'division_name': team['division_name'],
                'wins': team['wins'],
                'losses': team['losses'],
                'ties': team['ties'],
                'win_pct': win_pct,
                'div_wins': div_wins,
                'div_losses': div_losses,
                'div_pct': div_pct,
                'conf_wins': conf_wins,
                'conf_losses': conf_losses,
                'conf_pct': conf_pct,
                'points_diff': points_diff,
                'points_for': points_for
            })
        
        # Find division winners
        divisions = {}
        for team in teams_with_stats:
            div_id = team['division_id']
            if div_id not in divisions:
                divisions[div_id] = []
            divisions[div_id].append(team)
        
        # Get best team from each division using DIVISION tie-breakers
        division_winners = []
        for div_id, div_teams in divisions.items():
            # For division winners, use division record as primary tie-breaker
            sorted_teams = sorted(div_teams, key=lambda t: (
                -t['win_pct'],
                -t['div_pct'],      # Division record for same-division ties
                -t['conf_pct'],
                -t['points_diff'],
                -t['points_for']
            ))
            winner = sorted_teams[0]
            winner['is_division_winner'] = True
            division_winners.append(winner)
        
        # Sort division winners by CONFERENCE tie-breakers (not division)
        division_winners = sorted(division_winners, key=lambda t: (
            -t['win_pct'],
            -t['conf_pct'],     # Conference record for cross-division comparison
            -t['points_diff'],
            -t['points_for']
        ))
        
        # Get wild cards - use CONFERENCE tie-breakers (NOT division head-to-head)
        wildcard_candidates = [t for t in teams_with_stats 
                              if not any(t['team_id'] == w['team_id'] for w in division_winners)]
        
        # CRITICAL: For wild cards from different divisions, use CONFERENCE RECORD
        wildcard_candidates = sorted(wildcard_candidates, key=lambda t: (
            -t['win_pct'],
            -t['conf_pct'],     # Conference record is the tie-breaker for wild cards!
            -t['points_diff'],
            -t['points_for']
        ))
        
        # Combine seeds
        seeds = []
        for i, team in enumerate(division_winners, 1):
            team['seed_number'] = i
            team['seed_type'] = 'Division Winner'
            seeds.append(team)
        
        num_wildcards = playoff_spots - len(division_winners)
        for i, team in enumerate(wildcard_candidates[:num_wildcards], len(division_winners) + 1):
            team['seed_number'] = i
            team['seed_type'] = 'Wild Card'
            team['is_division_winner'] = False
            seeds.append(team)
        
        return seeds[:playoff_spots]
        
    except Exception as e:
        print(f"Error in calculate_conference_playoff_seeds: {e}")
        import traceback
        traceback.print_exc()
        return []


def sort_teams_with_tiebreakers(teams):
    """
    Sort teams WITHIN A DIVISION using tie-breaker rules.
    
    This should ONLY be used for teams in the same division.
    
    Tie-breaker order:
    1. Win percentage
    2. Head-to-head win percentage (if tied teams have played each other)
    3. Division win percentage
    4. Conference win percentage
    5. Points differential
    6. Points scored
    """
    def tiebreaker_key(team):
        # Calculate percentages for sorting
        h2h_pct = (team['h2h_wins'] / (team['h2h_wins'] + team['h2h_losses']) 
                   if (team['h2h_wins'] + team['h2h_losses']) > 0 else 0)
        div_pct = (team['div_wins'] / (team['div_wins'] + team['div_losses']) 
                   if (team['div_wins'] + team['div_losses']) > 0 else 0)
        conf_pct = (team['conf_wins'] / (team['conf_wins'] + team['conf_losses']) 
                    if (team['conf_wins'] + team['conf_losses']) > 0 else 0)
        
        return (
            -team['win_pct'],        # Primary: Win percentage (negative for descending)
            -h2h_pct,                # Tie-breaker 1: Head-to-head
            -div_pct,                # Tie-breaker 2: Division record
            -conf_pct,               # Tie-breaker 3: Conference record
            -team['points_diff'],    # Tie-breaker 4: Points differential
            -team['points_for']      # Tie-breaker 5: Points scored
        )
    
    return sorted(teams, key=tiebreaker_key)


def get_head_to_head_record(cursor, team_id, division_id, season, league_id):
    """Get head-to-head wins and losses against division opponents"""
    query = """
        SELECT 
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score > g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score > g.home_score) 
                THEN 1 ELSE 0 END) as wins,
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score < g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score < g.home_score) 
                THEN 1 ELSE 0 END) as losses
        FROM games g
        JOIN teams opp ON (
            CASE 
                WHEN g.home_team_id = ? THEN g.away_team_id
                ELSE g.home_team_id
            END = opp.team_id
        )
        WHERE (g.home_team_id = ? OR g.away_team_id = ?)
            AND opp.division_id = ?
            AND opp.team_id != ?
            AND g.game_status = 'COMPLETED'
            AND g.season = ?
            AND g.league_id = ?
    """
    cursor.execute(query, (team_id, team_id, team_id, team_id, team_id, 
                          team_id, team_id, division_id, team_id, season, league_id))
    result = cursor.fetchone()
    return (result['wins'] or 0, result['losses'] or 0)


def get_division_record(cursor, team_id, division_id, season, league_id):
    """Get wins and losses against division opponents"""
    query = """
        SELECT 
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score > g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score > g.home_score) 
                THEN 1 ELSE 0 END) as wins,
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score < g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score < g.home_score) 
                THEN 1 ELSE 0 END) as losses
        FROM games g
        JOIN teams opp ON (
            CASE 
                WHEN g.home_team_id = ? THEN g.away_team_id
                ELSE g.home_team_id
            END = opp.team_id
        )
        WHERE (g.home_team_id = ? OR g.away_team_id = ?)
            AND opp.division_id = ?
            AND opp.team_id != ?
            AND g.game_status = 'COMPLETED'
            AND g.season = ?
            AND g.league_id = ?
    """
    cursor.execute(query, (team_id, team_id, team_id, team_id, team_id, 
                          team_id, team_id, division_id, team_id, season, league_id))
    result = cursor.fetchone()
    return (result['wins'] or 0, result['losses'] or 0)


def get_conference_record(cursor, team_id, conference_id, season, league_id):
    """Get wins and losses against conference opponents"""
    query = """
        SELECT 
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score > g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score > g.home_score) 
                THEN 1 ELSE 0 END) as wins,
            SUM(CASE 
                WHEN (g.home_team_id = ? AND g.home_score < g.away_score) 
                  OR (g.away_team_id = ? AND g.away_score < g.home_score) 
                THEN 1 ELSE 0 END) as losses
        FROM games g
        JOIN teams opp ON (
            CASE 
                WHEN g.home_team_id = ? THEN g.away_team_id
                ELSE g.home_team_id
            END = opp.team_id
        )
        JOIN divisions d ON opp.division_id = d.division_id
        WHERE (g.home_team_id = ? OR g.away_team_id = ?)
            AND d.conference_id = ?
            AND opp.team_id != ?
            AND g.game_status = 'COMPLETED'
            AND g.season = ?
            AND g.league_id = ?
    """
    cursor.execute(query, (team_id, team_id, team_id, team_id, team_id, 
                          team_id, team_id, conference_id, team_id, season, league_id))
    result = cursor.fetchone()
    return (result['wins'] or 0, result['losses'] or 0)


def get_points_differential(cursor, team_id, season, league_id):
    """Get total points differential for the season"""
    query = """
        SELECT 
            SUM(CASE 
                WHEN g.home_team_id = ? THEN g.home_score - g.away_score
                ELSE g.away_score - g.home_score
            END) as points_diff
        FROM games g
        WHERE (g.home_team_id = ? OR g.away_team_id = ?)
            AND g.game_status = 'COMPLETED'
            AND g.season = ?
            AND g.league_id = ?
    """
    cursor.execute(query, (team_id, team_id, team_id, season, league_id))
    result = cursor.fetchone()
    return result['points_diff'] or 0


def get_points_scored(cursor, team_id, season, league_id):
    """Get total points scored for the season"""
    query = """
        SELECT 
            SUM(CASE 
                WHEN g.home_team_id = ? THEN g.home_score
                ELSE g.away_score
            END) as points_for
        FROM games g
        WHERE (g.home_team_id = ? OR g.away_team_id = ?)
            AND g.game_status = 'COMPLETED'
            AND g.season = ?
            AND g.league_id = ?
    """
    cursor.execute(query, (team_id, team_id, team_id, season, league_id))
    result = cursor.fetchone()
    return result['points_for'] or 0
