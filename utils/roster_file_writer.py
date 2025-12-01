# ========================================
# utils/roster_file_writer.py
# Version: 1.5 - Added write_week_roster_files wrapper method
# ========================================

"""
Roster File Writer Module

Creates team roster .nfl files in the format expected by the NFL Challenge game engine.
Files are named {team_name}.nfl and contain the full roster and starting lineup.

Format matches the original NFL Challenge roster template with:
- Header with year and team FULL name
- Player data in fixed columns (FILLER PLAYERS at end, not counted)
- Starters section
- Philosophy settings (extracted from teams table)
- Proper hex byte \x9b for special positions (5\x9b, 10\x9b)
- DOS line endings (\r\n) for NFL Challenge compatibility
"""

import sqlite3
import os
from typing import List, Dict, Optional, Set, Tuple


class RosterFileWriter:
    """Handles writing roster files for NFL Challenge"""
    
    def __init__(self, db_path: str):
        print(f"[ROSTER_WRITER] Initializing with db_path: {db_path}")
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def write_week_roster_files(self, season: int, week: int) -> bool:
        """
        Wrapper method for dashboard - gets league info automatically
        
        Args:
            season: Season number
            week: Week number
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[ROSTER_WRITER] ✓ write_week_roster_files called for season {season}, week {week}")
        
        # Get current league info
        league_info = self.get_current_league_info()
        if not league_info:
            print(f"[ROSTER_WRITER] ✗ No active league found")
            return False
        
        league_id, _, _, game_files_path = league_info
        
        # Call the main method with all required parameters
        return self.write_weekly_rosters(league_id, season, week, game_files_path)
    
    def write_weekly_rosters(self, league_id: int, season: int, week: int, output_directory: str = ".") -> bool:
        """
        Write roster files for all teams playing in the specified week
        
        Args:
            league_id: ID of the league
            season: Season number
            week: Week number
            output_directory: Directory to write the files
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[ROSTER_WRITER] ✓ Writing rosters: league_id={league_id}, season={season}, week={week}")
        
        try:
            # Step 1: Get teams playing this week
            teams_playing = self._get_teams_playing_this_week(league_id, season, week)
            print(f"[ROSTER_WRITER] Found {len(teams_playing)} teams playing this week")
            
            if not teams_playing:
                print(f"[ROSTER_WRITER] No teams playing in week {week}")
                return False
            
            # Step 2: Write roster file for each team
            files_written = 0
            for team_id, team_name in teams_playing:
                success = self._write_team_roster_file(league_id, team_id, team_name, season, output_directory)
                if success:
                    files_written += 1
                    print(f"[ROSTER_WRITER] ✓ Wrote roster file for {team_name}")
                else:
                    print(f"[ROSTER_WRITER] ✗ Failed to write roster file for {team_name}")
            
            print(f"[ROSTER_WRITER] ✓ Successfully wrote {files_written} roster files")
            return files_written > 0
            
        except Exception as e:
            print(f"[ROSTER_WRITER] ✗ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
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
            print(f"[ROSTER_WRITER] Error getting league info: {e}")
            return None
    
    def _get_teams_playing_this_week(self, league_id: int, season: int, week: int) -> List[tuple]:
        """Get all teams that have games this week"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get unique teams playing this week
            cursor.execute("""
                SELECT DISTINCT t.team_id, t.team_name
                FROM games g
                JOIN teams t ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
                WHERE g.league_id = ? 
                  AND g.season = ? 
                  AND g.week = ?
                  AND g.game_status IN ('SCHEDULED', 'IN_PROGRESS')
                ORDER BY t.team_name
            """, (league_id, season, week))
            
            teams = cursor.fetchall()
            return [(team['team_id'], team['team_name']) for team in teams]
    
    def _write_team_roster_file(self, league_id: int, team_id: int, team_name: str, season: int, output_directory: str) -> bool:
        """Write a single team's roster file"""
        try:
            # Get team full name for header
            team_full_name = self._get_team_full_name(league_id, team_id)
            
            # Get team philosophies
            offensive_philosophy, defensive_philosophy = self._get_team_philosophies(league_id, team_id)
            
            # Get team roster data
            roster_data = self._get_team_roster_data(league_id, team_id)
            if not roster_data:
                print(f"[ROSTER_WRITER] No roster data found for {team_name}")
                return False
            
            # Get starters data
            starters_data = self._get_team_starters_data(league_id, team_id)
            
            # Create file content using full team name for header and team philosophies
            file_content = self._format_roster_file(team_full_name, season, roster_data, starters_data, 
                                                  offensive_philosophy, defensive_philosophy)
            
            # Write file using team_name for filename
            filename = f"{team_name}.nfl"
            file_path = os.path.join(output_directory, filename)
            
            # Create directory if needed
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            
            # Write with latin-1 encoding to properly handle \x9b byte
            with open(file_path, 'w', encoding='latin-1') as f:
                f.write(file_content)
            
            print(f"[ROSTER_WRITER] ✓ Wrote {filename} (Offense: {offensive_philosophy}, Defense: {defensive_philosophy})")
            return True
            
        except Exception as e:
            print(f"[ROSTER_WRITER] ✗ Error writing roster for {team_name}: {e}")
            return False
    
    def _get_team_full_name(self, league_id: int, team_id: int) -> str:
        """Get the full team name for the header"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT full_name 
                FROM teams 
                WHERE team_id = ? AND league_id = ? AND is_active = TRUE
            """, (team_id, league_id))
            
            result = cursor.fetchone()
            return result['full_name'] if result else "Unknown Team"
    
    def _get_team_philosophies(self, league_id: int, team_id: int) -> Tuple[str, str]:
        """Get team's offensive and defensive philosophies"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT offensive_philosophy, defensive_philosophy
                FROM teams 
                WHERE team_id = ? AND league_id = ? AND is_active = TRUE
            """, (team_id, league_id))
            
            result = cursor.fetchone()
            if result:
                offensive = result['offensive_philosophy'] or 'Conservative'
                defensive = result['defensive_philosophy'] or 'Conservative'
                print(f"[ROSTER_WRITER] Team philosophies - Offense: {offensive}, Defense: {defensive}")
                return offensive, defensive
            else:
                print(f"[ROSTER_WRITER] No philosophy data found, using defaults")
                return 'Conservative', 'Conservative'
    
    def _get_team_roster_data(self, league_id: int, team_id: int) -> List[Dict]:
        """Get roster data for a team - separate real players from filler players"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all roster data
            cursor.execute("""
                SELECT DISTINCT
                    r.jersey_number,
                    pos.position_code as position,
                    p.height_inches,
                    p.weight,
                    p.years_experience,
                    p.speed_40_time,
                    p.skill_run,
                    p.skill_receive,
                    p.skill_block,
                    p.skill_pass,
                    p.skill_kick,
                    p.display_name,
                    p.player_id
                FROM roster r
                JOIN players p ON r.player_id = p.player_id
                JOIN positions pos ON p.position_id = pos.position_id
                WHERE r.team_id = ? 
                  AND r.league_id = ?
                  AND r.is_active = TRUE
                  AND p.player_status = 'ACTIVE'
                ORDER BY r.jersey_number
            """, (team_id, league_id))
            
            players = cursor.fetchall()
            
            # Separate real players from filler players
            real_players = []
            filler_players = []
            
            for player in players:
                player_dict = dict(player)
                is_filler = 'FILLER PLAYER' in player_dict['display_name'].upper()
                
                if is_filler:
                    filler_players.append(player_dict)
                    print(f"[ROSTER_WRITER] Added FILLER: #{player_dict['jersey_number']} {player_dict['display_name']}")
                else:
                    real_players.append(player_dict)
                    print(f"[ROSTER_WRITER] Added player: #{player_dict['jersey_number']} {player_dict['display_name']} ({player_dict['position']})")
            
            # Return real players first, then filler players at the end
            return real_players + filler_players
    
    def _get_team_starters_data(self, league_id: int, team_id: int) -> Dict[str, int]:
        """Get starting lineup data for a team"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get starters (depth_chart_order = 1)
            cursor.execute("""
                SELECT 
                    pos.position_code,
                    r.jersey_number
                FROM roster r
                JOIN players p ON r.player_id = p.player_id
                JOIN positions pos ON r.position_on_team_id = pos.position_id
                WHERE r.team_id = ? 
                  AND r.league_id = ?
                  AND r.is_active = TRUE
                  AND r.depth_chart_order = 1
                  AND p.player_status = 'ACTIVE'
                ORDER BY pos.position_code
            """, (team_id, league_id))
            
            starters = cursor.fetchall()
            return {starter['position_code']: starter['jersey_number'] for starter in starters}
    
    def _format_roster_file(self, team_full_name: str, season: int, roster_data: List[Dict], 
                           starters_data: Dict[str, int], offensive_philosophy: str, defensive_philosophy: str) -> str:
        """Format the roster data into NFL Challenge format"""
        
        lines = []
        
        # Count only real players (not FILLER PLAYERS)
        real_player_count = sum(1 for player in roster_data if 'FILLER PLAYER' not in player['display_name'].upper())
        
        # Header line - centered team full name with year
        header = f"{season} {team_full_name}"
        lines.append(f"{header:>45}")
        
        # Column headers - use real player count only
        lines.append("  No.  Pos   Ht.   Wt. Yrs. Spd  Run  Rcv  Blk  Pass Kick    Players: {}".format(real_player_count))
        
        # Separator line
        lines.append("-----------------------------------------------------------------------------")
        
        # Player data (real players first, then filler players at end)
        for player in roster_data:
            # Format height as feet'inches"
            height_inches = player['height_inches']
            feet = height_inches // 12
            inches = height_inches % 12
            
            # Format height to exactly 5 characters:
            # Single digit inches: "6' 3"" (with space)  
            # Double digit inches: "5'11"" (no space)
            if inches < 10:
                height_str = f"{feet}' {inches}\""
            else:
                height_str = f"{feet}'{inches}\""
            
            # Format speed (convert to 1 decimal place)
            speed = player['speed_40_time'] if player['speed_40_time'] else 5.0
            
            # Format player line with exact spacing
            line = "   {:<4}{:<2}   {:>5} {:>4} {:>3} {:>4} {:>3} {:>4} {:>4} {:>4} {:>4}   {}".format(
                player['jersey_number'],
                player['position'],
                height_str,
                player['weight'],
                player['years_experience'],
                f"{speed:.1f}",
                player['skill_run'],
                player['skill_receive'],
                player['skill_block'],
                player['skill_pass'],
                player['skill_kick'],
                player['display_name']
            )
            lines.append(line)
        
        # Empty line before starters
        lines.append("")
        
        # Starters section
        lines.append("STARTERS")
        
        # Default starter positions in order (using hex byte \x9b for special positions)
        starter_positions = [
            'LT', 'LG', 'RG', 'RT', 'C', 
            'TE', 'TE2', 'TE3', 'FL', 'SE', 'WR3', 'FB', 'HB', 'QB',
            'LE', 'LDT', 'R/NT', 'RE', 'LOLB', 'LILB', 'RMLB', 'ROLB', 'LCB', 'RCB', 'SS', 'FS',
            '5\x9b', '10\x9b', 'K', 'P', 'PR', 'KR'  # Using hex byte \x9b as NFL Challenge expects
        ]
        
        # Write starters (use position mappings for NFL Challenge positions)
        position_mappings = self._get_position_mappings()
        
        for pos in starter_positions:
            # Try to find a starter for this position
            jersey = None
            
            # First, try exact match
            if pos in starters_data:
                jersey = starters_data[pos]
            else:
                # Try mapping
                mapped_pos = position_mappings.get(pos)
                if mapped_pos and mapped_pos in starters_data:
                    jersey = starters_data[mapped_pos]
                else:
                    # Default to first player at similar position
                    jersey = self._find_default_starter(pos, roster_data)
            
            if jersey:
                lines.append(f"{pos:<4}  {jersey}")
                # Debug output for special positions
                if pos in ['5\x9b', '10\x9b']:
                    print(f"[ROSTER_WRITER] Special position {repr(pos)} assigned jersey #{jersey}")
            else:
                lines.append(f"{pos:<4}  1")  # Default to jersey #1 if no match
                print(f"[ROSTER_WRITER] No player found for position {repr(pos)}, defaulting to jersey #1")
        
        # Philosophy sections - using team's actual philosophies
        lines.append("Offense:")
        lines.append(offensive_philosophy)
        lines.append("Defense:")
        lines.append(defensive_philosophy)
        
        return "\r\n".join(lines)
    
    def _get_position_mappings(self) -> Dict[str, str]:
        """Map NFL Challenge positions to database positions"""
        return {
            'LT': 'LT', 'LG': 'LG', 'RG': 'RG', 'RT': 'RT', 'C': 'C',
            'TE': 'TE', 'TE2': 'TE', 'TE3': 'TE',
            'FL': 'WR', 'SE': 'WR', 'WR3': 'WR',
            'FB': 'FB', 'HB': 'RB', 'QB': 'QB',
            'LE': 'LE', 'LDT': 'LDT', 'R/NT': 'NT', 'RE': 'RE',
            'LOLB': 'LOLB', 'LILB': 'LILB', 'RMLB': 'RMLB', 'ROLB': 'ROLB',
            'LCB': 'LCB', 'RCB': 'RCB', 'SS': 'SS', 'FS': 'FS',
            '5\x9b': 'DB',  # 5<9b> -> DB (defensive back)
            '10\x9b': 'DB', # 10<9b> -> DB (defensive back)
            'K': 'K', 'P': 'P', 'PR': 'PR', 'KR': 'KR'
        }
    
    def _find_default_starter(self, position: str, roster_data: List[Dict]) -> Optional[int]:
        """Find a default starter for a position"""
        
        # Position fallbacks
        fallbacks = {
            'TE2': ['TE', 'FB'],
            'TE3': ['TE', 'FB'],
            'WR3': ['WR'],
            'FL': ['WR'],
            'SE': ['WR'],
            'HB': ['RB'],
            'LDT': ['DT', 'NT'],
            'R/NT': ['NT', 'DT'],
            '5\x9b': ['DB', 'CB', 'SS'],  # 5<9b> -> defensive back positions
            '10\x9b': ['DB', 'CB', 'FS'], # 10<9b> -> defensive back positions
            'PR': ['WR', 'RB', 'DB'],
            'KR': ['WR', 'RB', 'DB']
        }
        
        # Try the position itself first
        search_positions = [position]
        if position in fallbacks:
            search_positions.extend(fallbacks[position])
        
        for search_pos in search_positions:
            for player in roster_data:
                if player['position'] == search_pos:
                    return player['jersey_number']
        
        return None


def main():
    """Test/example usage"""
    writer = RosterFileWriter("pynfl.db")
    
    # Write rosters for teams playing in week 1
    success = writer.write_weekly_rosters(league_id=1, season=1, week=1, output_directory=".")
    print(f"Roster write successful: {success}")


if __name__ == "__main__":
    main()
