# ========================================
# utils/schedule_file_writer.py
# Version: 1.1 - Added write_week_schedule_file wrapper method
# ========================================

"""
Schedule File Writer Module

Creates season.nfl files containing the weekly schedule in the format
expected by the NFL Challenge game engine.

File format:
- First line: number of games
- Each subsequent line: home_team away_team (separated by space)
"""

import sqlite3
import os
from typing import List, Tuple, Optional


class ScheduleFileWriter:
    """Handles writing schedule files for NFL Challenge"""
    
    def __init__(self, db_path: str):
        print(f"[SCHEDULE_WRITER] Initializing with db_path: {db_path}")
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def write_week_schedule_file(self, season: int, week: int) -> bool:
        """
        Wrapper method for dashboard - gets league info automatically
        
        Args:
            season: Season number
            week: Week number
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[SCHEDULE_WRITER] ✓ write_week_schedule_file called for season {season}, week {week}")
        
        # Get current league info
        league_info = self.get_current_league_info()
        if not league_info:
            print(f"[SCHEDULE_WRITER] ✗ No active league found")
            return False
        
        league_id, _, _, game_files_path = league_info
        
        # Call the main method with all required parameters
        return self.write_weekly_schedule(league_id, season, week, game_files_path)
    
    def write_weekly_schedule(self, league_id: int, season: int, week: int, output_directory: str = ".") -> bool:
        """
        Write the weekly schedule to season.nfl file
        
        Args:
            league_id: ID of the league
            season: Season number
            week: Week number
            output_directory: Directory to write the file (default: current directory)
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[SCHEDULE_WRITER] ✓ Writing schedule: league_id={league_id}, season={season}, week={week}")
        
        try:
            # Step 1: Get games for the specified week
            games = self._get_weekly_games(league_id, season, week)
            print(f"[SCHEDULE_WRITER] Found {len(games)} games for week {week}")
            
            if not games:
                print(f"[SCHEDULE_WRITER] No games found for season {season}, week {week}")
                return False
            
            # Step 2: Format games for output
            game_lines = self._format_games(games)
            print(f"[SCHEDULE_WRITER] Formatted {len(game_lines)} game lines")
            
            # Step 3: Write to file
            output_path = os.path.join(output_directory, "season.nfl")
            self._write_schedule_file(output_path, game_lines)
            print(f"[SCHEDULE_WRITER] ✓ Successfully wrote schedule to {output_path}")
            
            return True
            
        except Exception as e:
            print(f"[SCHEDULE_WRITER] ✗ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_weekly_games(self, league_id: int, season: int, week: int) -> List[dict]:
        """Get all games for the specified week"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for games in the specified week with team names
            cursor.execute("""
                SELECT 
                    g.game_id,
                    g.week,
                    g.game_type,
                    g.game_status,
                    home.team_name as home_team_name,
                    away.team_name as away_team_name,
                    g.day_of_week,
                    g.game_notes
                FROM games g
                JOIN teams home ON g.home_team_id = home.team_id
                JOIN teams away ON g.away_team_id = away.team_id
                WHERE g.league_id = ? 
                  AND g.season = ? 
                  AND g.week = ?
                  AND g.game_status IN ('SCHEDULED', 'IN_PROGRESS')
                ORDER BY g.game_type, g.day_of_week, g.game_id
            """, (league_id, season, week))
            
            games = cursor.fetchall()
            
            # Convert to list of dictionaries
            game_list = []
            for game in games:
                game_dict = dict(game)
                game_list.append(game_dict)
                print(f"[SCHEDULE_WRITER] Game: {game_dict['away_team_name']} @ {game_dict['home_team_name']} ({game_dict['game_type']})")
            
            return game_list
    
    def _format_games(self, games: List[dict]) -> List[str]:
        """Format games into the required string format"""
        game_lines = []
        
        for game in games:
            home_team = game['home_team_name']
            away_team = game['away_team_name']
            
            # Format: home_team away_team (separated by space)
            game_line = f"{home_team} {away_team}"
            game_lines.append(game_line)
            print(f"[SCHEDULE_WRITER] Formatted: {game_line}")
        
        return game_lines
    
    def _write_schedule_file(self, file_path: str, game_lines: List[str]):
        """Write the schedule file"""
        print(f"[SCHEDULE_WRITER] Writing to file: {file_path}")
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[SCHEDULE_WRITER] Created directory: {directory}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # First line: number of games
            f.write(f"{len(game_lines)}\n")
            print(f"[SCHEDULE_WRITER] Wrote game count: {len(game_lines)}")
            
            # Each subsequent line: home_team away_team
            for game_line in game_lines:
                f.write(f"{game_line}\n")
        
        print(f"[SCHEDULE_WRITER] ✓ File written successfully")
    
    def get_current_league_info(self) -> Optional[Tuple[int, int, int, str]]:
        """Get current league, season, and week information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, league_name, current_season, current_week, game_files_path
                    FROM leagues 
                    WHERE is_active = TRUE 
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if result:
                    return (result['league_id'], result['current_season'], 
                           result['current_week'], result['game_files_path'] or ".")
                else:
                    return None
                    
        except Exception as e:
            print(f"[SCHEDULE_WRITER] Error getting league info: {e}")
            return None


def main():
    """Test/example usage"""
    writer = ScheduleFileWriter("pynfl.db")
    
    # Get current league info
    league_info = writer.get_current_league_info()
    if league_info:
        league_id, season, week, game_files_path = league_info
        print(f"Current league: {league_id}, Season {season}, Week {week}")
        
        # Write schedule for current week
        success = writer.write_weekly_schedule(league_id, season, week, game_files_path)
        print(f"Schedule write successful: {success}")
    else:
        print("No active league found")


if __name__ == "__main__":
    main()
