# ========================================
# schedule/schedule_generator.py
# ========================================

"""
Schedule Generation Module

Handles generation of preseason, regular season, and playoff schedules
based on league configuration and team structure.
"""

import sqlite3
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import QMessageBox


class ScheduleGenerator:
    """Handles schedule generation operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_preseason_schedule(self, league_id: int, season: int) -> bool:
        """
        Generate preseason schedule for the specified league and season
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # TODO: Implement preseason schedule generation
            # - Get league settings (number of preseason games)
            # - Get teams and divisions
            # - Create preseason matchups (usually cross-division/conference)
            # - Insert games into database
            print(f"Generating preseason schedule for league {league_id}, season {season}")
            return True
            
        except Exception as e:
            print(f"Error generating preseason schedule: {str(e)}")
            return False
    
    def generate_regular_season_schedule(self, league_id: int, season: int) -> bool:
        """
        Generate regular season schedule for the specified league and season
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # TODO: Implement regular season schedule generation
            # - Get league settings (games per season, division structure)
            # - Generate division games (home/away if enabled)
            # - Generate conference games
            # - Generate inter-conference games
            # - Balance home/away games
            # - Distribute games across weeks
            # - Insert games into database
            print(f"Generating regular season schedule for league {league_id}, season {season}")
            return True
            
        except Exception as e:
            print(f"Error generating regular season schedule: {str(e)}")
            return False
    
    def generate_playoff_schedule(self, league_id: int, season: int) -> bool:
        """
        Generate playoff schedule based on regular season standings
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # TODO: Implement playoff schedule generation
            # - Get league playoff settings (teams per conference, weeks)
            # - Calculate standings and determine playoff teams
            # - Create playoff bracket based on seeding
            # - Generate wildcard, divisional, conference, and championship games
            # - Insert playoff games into database
            print(f"Generating playoff schedule for league {league_id}, season {season}")
            return True
            
        except Exception as e:
            print(f"Error generating playoff schedule: {str(e)}")
            return False
    
    def clear_schedule(self, league_id: int, season: int, schedule_type: str = "ALL") -> bool:
        """
        Clear existing schedule for the specified league and season
        
        Args:
            league_id: ID of the league
            season: Season number
            schedule_type: Type of schedule to clear ("ALL", "PRESEASON", "REGULAR", "PLAYOFFS")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if schedule_type == "ALL":
                    # Clear all games for the season
                    cursor.execute("""
                        DELETE FROM games 
                        WHERE league_id = ? AND season = ?
                    """, (league_id, season))
                    
                elif schedule_type == "PRESEASON":
                    # Clear only preseason games
                    cursor.execute("""
                        DELETE FROM games 
                        WHERE league_id = ? AND season = ? AND game_type = 'PRESEASON'
                    """, (league_id, season))
                    
                elif schedule_type == "REGULAR":
                    # Clear only regular season games
                    cursor.execute("""
                        DELETE FROM games 
                        WHERE league_id = ? AND season = ? AND game_type = 'REGULAR'
                    """, (league_id, season))
                    
                elif schedule_type == "PLAYOFFS":
                    # Clear all playoff games
                    cursor.execute("""
                        DELETE FROM games 
                        WHERE league_id = ? AND season = ? 
                          AND game_type IN ('WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL')
                    """, (league_id, season))
                
                conn.commit()
                deleted_count = cursor.rowcount
                print(f"Cleared {deleted_count} {schedule_type} games for league {league_id}, season {season}")
                return True
            
        except Exception as e:
            print(f"Error clearing schedule: {str(e)}")
            return False
    
    def validate_league_structure(self, league_id: int) -> bool:
        """
        Validate that league has proper structure for schedule generation
        
        Args:
            league_id: ID of the league
            
        Returns:
            True if league structure is valid, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if league exists
                cursor.execute("""
                    SELECT league_id FROM leagues 
                    WHERE league_id = ? AND is_active = TRUE
                """, (league_id,))
                
                if not cursor.fetchone():
                    print(f"League {league_id} not found or not active")
                    return False
                
                # Check if league has teams
                cursor.execute("""
                    SELECT COUNT(*) as team_count FROM teams 
                    WHERE league_id = ? AND is_active = TRUE
                """, (league_id,))
                
                team_count = cursor.fetchone()['team_count']
                if team_count < 4:
                    print(f"League has only {team_count} teams - need at least 4 for scheduling")
                    return False
                
                if team_count % 2 != 0:
                    print(f"League has {team_count} teams - need even number for balanced schedule")
                    return False
                
                # Check conference/division structure
                cursor.execute("""
                    SELECT COUNT(DISTINCT conference_id) as conf_count,
                           COUNT(DISTINCT division_id) as div_count
                    FROM teams 
                    WHERE league_id = ? AND is_active = TRUE
                      AND conference_id IS NOT NULL
                """, (league_id,))
                
                structure = cursor.fetchone()
                if structure['conf_count'] < 1:
                    print("League has no conferences defined")
                    return False
                
                print(f"League structure validated: {team_count} teams, "
                      f"{structure['conf_count']} conferences, {structure['div_count']} divisions")
                return True
                
        except Exception as e:
            print(f"Error validating league structure: {str(e)}")
            return False
    
    def get_schedule_info(self, league_id: int, season: int) -> Dict:
        """
        Get information about existing schedule
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            Dictionary with schedule information
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get game counts by type
                cursor.execute("""
                    SELECT 
                        game_type,
                        COUNT(*) as game_count,
                        SUM(CASE WHEN game_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count
                    FROM games 
                    WHERE league_id = ? AND season = ?
                    GROUP BY game_type
                """, (league_id, season))
                
                results = cursor.fetchall()
                
                info = {
                    'preseason_games': 0,
                    'regular_season_games': 0,
                    'playoff_games': 0,
                    'completed_games': 0,
                    'has_schedule': False
                }
                
                total_games = 0
                for result in results:
                    game_type = result['game_type']
                    game_count = result['game_count']
                    completed_count = result['completed_count']
                    
                    total_games += game_count
                    info['completed_games'] += completed_count
                    
                    if game_type == 'PRESEASON':
                        info['preseason_games'] = game_count
                    elif game_type == 'REGULAR':
                        info['regular_season_games'] = game_count
                    elif game_type in ['WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL']:
                        info['playoff_games'] += game_count
                
                info['has_schedule'] = total_games > 0
                return info
                
        except Exception as e:
            print(f"Error getting schedule info: {str(e)}")
            return {
                'preseason_games': 0,
                'regular_season_games': 0,
                'playoff_games': 0,
                'completed_games': 0,
                'has_schedule': False
            }


def main():
    """Test/example usage"""
    generator = ScheduleGenerator("pynfl.db")
    
    # Example usage
    league_id = 1
    season = 1
    
    if generator.validate_league_structure(league_id):
        print("Generating schedules...")
        
        # Generate preseason
        if generator.generate_preseason_schedule(league_id, season):
            print("✓ Preseason schedule generated")
        
        # Generate regular season
        if generator.generate_regular_season_schedule(league_id, season):
            print("✓ Regular season schedule generated")
        
        # Get schedule info
        info = generator.get_schedule_info(league_id, season)
        print(f"Schedule info: {info}")
        
        # Playoffs would be generated after regular season is complete
        # generator.generate_playoff_schedule(league_id, season)
        
    else:
        print("League structure validation failed")


if __name__ == "__main__":
    main()
