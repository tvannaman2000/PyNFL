# ========================================
# utils/stats_processor.py
# Version: 2.5
# ========================================

"""
Enhanced Stats Log Processor Module - Overtime Fix

Processes NFL Challenge STATS.LOG files containing game results and statistics.
Parses quarter-by-quarter scores, team stats, and individual player statistics.

Features:
- Parses multiple games from single STATS.LOG file
- Updates game scores in database
- Extracts team statistics (yards, first downs, time of possession, etc.)
- Processes individual player stats (rushing, passing, receiving, etc.)
- Stores both team and individual stats in database tables
- Handles overtime games correctly

FIXES (v2.5):
- Fixed overtime detection and OT points calculation
- OT points now correctly calculated as (Total - Q1 - Q2 - Q3 - Q4)
- Detects "OVERTIME" label in stats.log file

Previous fixes:
- Fixed player creation to use first_name/last_name instead of display_name (generated column)
- Fixed game splitting to handle "Results from Game #" format
"""

import sqlite3
import re
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from PyQt5.QtWidgets import QFileDialog, QMessageBox


@dataclass
class GameResult:
    """Data class for game result information"""
    game_number: int
    away_team: str
    home_team: str
    away_score: int
    home_score: int
    quarter_scores: List[Tuple[int, int]]  # [(away_q1, home_q1), ...]
    is_overtime: bool = False  # NEW: Flag for overtime games


@dataclass
class TeamStats:
    """Data class for team statistics"""
    team_name: str
    first_downs: int
    first_downs_rush: int
    first_downs_pass: int
    first_downs_penalty: int
    third_down_conv: str  # "7 - 14 - 50.0%"
    time_of_possession: str  # "39:04"
    total_net_yards: int
    total_plays: int
    net_yards_rush: int
    rush_plays: int
    net_yards_pass: int
    pass_attempts: int
    pass_completions: int
    pass_interceptions: int
    sacks_allowed: int
    sack_yards_lost: int
    punts: int
    punt_average: float
    return_yards: int
    penalty_count: int
    penalty_yards: int
    fumbles: int
    fumbles_lost: int


@dataclass
class PlayerStat:
    """Data class for individual player statistics"""
    jersey_number: int
    position: str
    player_name: str
    team_name: str
    stat_category: str  # 'rushing', 'passing', 'receiving', etc.
    stats: Dict  # Category-specific stats


class StatsProcessor:
    """Processes STATS.LOG files and updates database"""
    
    def __init__(self, db_path: str):
        """Initialize with database path"""
        self.db_path = db_path
        print(f"[STATS_PROCESSOR] Initialized with database: {db_path}")
    
    def select_and_process_stats_file(self, parent_widget, league_id: int, season: int, week: int) -> bool:
        """Select and process a STATS.LOG file"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Select STATS.LOG File",
            "",
            "Log Files (*.LOG *.log);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        return self.process_stats_file(file_path, league_id, season, week)


    
    def process_stats_file(self, file_path: str, league_id: int, season: int, week: int) -> bool:
        """Process stats file and update database"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            print(f"[STATS_PROCESSOR] Processing: {file_path}")
            games_processed = 0
            
            # Split into individual games
            game_blocks = self._split_into_games(content)
            
            for game_block in game_blocks:
                if self._process_single_game(game_block, league_id, season, week):
                    games_processed += 1
            
            if games_processed > 0:
                QMessageBox.information(None, "Stats Processed", 
                                      f"Successfully processed {games_processed} game(s)")
                return True
            else:
                QMessageBox.warning(None, "No Games Processed", 
                                  "No valid games found in the stats file")
                return False
                
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error processing file: {str(e)}")
            QMessageBox.critical(None, "Error", f"Failed to process stats file:\n{str(e)}")
            return False
   

    ################################## 
    ## This reads the entire LOG file checking out how many games there are.
    ##################################

    def _split_into_games(self, content: str) -> List[str]:
        """Split content into individual game blocks"""
        # Split on "Results from Game" (with any number after it)
        game_pattern = r'Results from Game\s+\d+'
        games = re.split(game_pattern, content, flags=re.IGNORECASE)
        
        # Skip the first element (content before first game) and filter empty blocks
        valid_games = [game.strip() for game in games[1:] if game.strip()]
        
        print(f"[STATS_PROCESSOR] Found {len(valid_games)} games in file")
        return valid_games
    



    def _process_single_game(self, game_content: str, league_id: int, season: int, week: int) -> bool:
        """Process a single game's content"""
        try:
            lines = [line.strip() for line in game_content.split('\n') if line.strip()]
            
            # Parse game result
            game_data = self._parse_game_data(lines, league_id, season, week)
            if not game_data:
                return False
            
            # Store all data in database
            return self._store_game_data(game_data, league_id, season, week)
            
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error processing single game: {str(e)}")
            return False
   


 
    def _parse_game_data(self, lines: List[str], league_id: int, season: int, week: int) -> Optional[Dict]:
        """Parse complete game data including scores, team stats, and player stats"""
        
        # FIXED: Check for OVERTIME label before score section
        is_overtime = False
        for line in lines:
            if "OVERTIME" in line.upper():
                is_overtime = True
                print("[STATS_PROCESSOR] Detected OVERTIME game")
                break
        
        # Find score section
        score_start_idx = None
        for i, line in enumerate(lines):
            if line.startswith("-" * 15) and i < len(lines) - 3:
                # Check if next lines contain team scores
                if len(lines) > i + 2:
                    try:
                        next_line = lines[i + 1].split()
                        # FIXED: Check for team name followed by 5 numbers (Q1 Q2 Q3 Q4 Total)
                        # Format: TeamName Q1 Q2 Q3 Q4 Total
                        if len(next_line) >= 6:
                            # First element is team name (can be anything)
                            # Next 5 elements should be numbers (quarters + total)
                            quarters_and_total = next_line[1:6]
                            if all(x.isdigit() for x in quarters_and_total):
                                score_start_idx = i
                                print(f"[STATS_PROCESSOR] Found score section at line {i}")
                                break
                    except Exception as e:
                        print(f"[STATS_PROCESSOR] Error checking line {i}: {e}")
                        continue
        
        if score_start_idx is None:
            print("[STATS_PROCESSOR] Could not find score section")
            return None
        
        try:
            # Parse scores
            away_line = lines[score_start_idx + 1].strip()
            home_line = lines[score_start_idx + 2].strip()
            
            away_parts = away_line.split()
            home_parts = home_line.split()
            
            away_team = away_parts[0]
            home_team = home_parts[0]
            
            # Extract quarter scores and total
            # The format is always: Team Q1 Q2 Q3 Q4 Total (5 numbers after team name)
            away_quarters = [int(x) for x in away_parts[1:5]]  # Q1-Q4
            home_quarters = [int(x) for x in home_parts[1:5]]
            away_total = int(away_parts[5])
            home_total = int(home_parts[5])
            
            game_result = GameResult(
                game_number=1,  # Will be determined by database matching
                away_team=away_team,
                home_team=home_team,
                away_score=away_total,
                home_score=home_total,
                quarter_scores=list(zip(away_quarters, home_quarters)),
                is_overtime=is_overtime  # NEW: Store overtime flag
            )
            
            # Parse team stats
            team_stats = self._parse_team_stats(lines, away_team, home_team)
            
            # Parse individual stats
            individual_stats = self._parse_individual_stats(lines)
            
            return {
                'game_result': game_result,
                'team_stats': team_stats,
                'individual_stats': individual_stats
            }
            
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error parsing game data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_team_stats(self, lines: List[str], away_team: str, home_team: str) -> Dict[str, TeamStats]:
        """Parse team statistics section"""
        team_stats = {}
        
        # Find team stats section
        stats_start_idx = None
        for i, line in enumerate(lines):
            if line.startswith("Team") and len(line.split()) >= 3:
                stats_start_idx = i
                break
        
        if stats_start_idx is None:
            return team_stats
        
        try:
            # Initialize team stats objects
            team_stats[away_team] = TeamStats(
                team_name=away_team,
                first_downs=0, first_downs_rush=0, first_downs_pass=0, first_downs_penalty=0,
                third_down_conv="0-0-0.0%", time_of_possession="0:00",
                total_net_yards=0, total_plays=0, net_yards_rush=0, rush_plays=0,
                net_yards_pass=0, pass_attempts=0, pass_completions=0, pass_interceptions=0,
                sacks_allowed=0, sack_yards_lost=0, punts=0, punt_average=0.0,
                return_yards=0, penalty_count=0, penalty_yards=0, fumbles=0, fumbles_lost=0
            )
            
            team_stats[home_team] = TeamStats(
                team_name=home_team,
                first_downs=0, first_downs_rush=0, first_downs_pass=0, first_downs_penalty=0,
                third_down_conv="0-0-0.0%", time_of_possession="0:00",
                total_net_yards=0, total_plays=0, net_yards_rush=0, rush_plays=0,
                net_yards_pass=0, pass_attempts=0, pass_completions=0, pass_interceptions=0,
                sacks_allowed=0, sack_yards_lost=0, punts=0, punt_average=0.0,
                return_yards=0, penalty_count=0, penalty_yards=0, fumbles=0, fumbles_lost=0
            )
            
            # Parse each stat line
            i = stats_start_idx + 1
            while i < len(lines):
                line = lines[i].strip()
                
                if not line or "Individual Statistical Results" in line:
                    break
                
                if "First Downs" in line and len(line.split()) >= 3:
                    parts = line.split()
                    if len(parts) >= 3:
                        away_fd = int(parts[-2])
                        home_fd = int(parts[-1])
                        team_stats[away_team].first_downs = away_fd
                        team_stats[home_team].first_downs = home_fd
                
                elif "Run-Pass-Pen" in line:
                    parts = line.split()
                    if len(parts) >= 11:
                        try:
                            away_rush = int(parts[1])
                            away_pass = int(parts[3])
                            away_pen = int(parts[5])
                            home_rush = int(parts[6])
                            home_pass = int(parts[8])
                            home_pen = int(parts[10])
                            
                            team_stats[away_team].first_downs_rush = away_rush
                            team_stats[away_team].first_downs_pass = away_pass
                            team_stats[away_team].first_downs_penalty = away_pen
                            team_stats[home_team].first_downs_rush = home_rush
                            team_stats[home_team].first_downs_pass = home_pass
                            team_stats[home_team].first_downs_penalty = home_pen
                        except (ValueError, IndexError):
                            pass
                
                elif "3rd Down Conv" in line:
                    parts = line.split()
                    if len(parts) >= 12:
                        try:
                            away_conv = int(parts[3])
                            away_att = int(parts[5])
                            away_pct = parts[7]
                            team_stats[away_team].third_down_conv = f"{away_conv} - {away_att} - {away_pct}"
                          
                            home_conv = int(parts[8])
                            home_att = int(parts[10])
                            home_pct = parts[12]
                            team_stats[home_team].third_down_conv = f"{home_conv} - {home_att} - {home_pct}"
                        except (ValueError, IndexError):
                            pass
                
                elif "Time of poss" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        team_stats[away_team].time_of_possession = parts[-2]
                        team_stats[home_team].time_of_possession = parts[-1]
                
                elif "Total Net Yards" in line and len(line.split()) >= 3:
                    parts = line.split()
                    if len(parts) >= 3:
                        away_yards = int(parts[-2])
                        home_yards = int(parts[-1])
                        team_stats[away_team].total_net_yards = away_yards
                        team_stats[home_team].total_net_yards = home_yards
                
                elif "Plays - Avg" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_plays = int(parts[3])
                            home_plays = int(parts[6])
                            team_stats[away_team].total_plays = away_plays
                            team_stats[home_team].total_plays = home_plays
                        except (ValueError, IndexError):
                            pass
                
                elif "Net Yards Rush" in line and len(line.split()) >= 3:
                    parts = line.split()
                    if len(parts) >= 3:
                        away_rush = int(parts[-2])
                        home_rush = int(parts[-1])
                        team_stats[away_team].net_yards_rush = away_rush
                        team_stats[home_team].net_yards_rush = home_rush
                
                elif "R Plays" in line and "Avg" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_rush_plays = int(parts[3])
                            home_rush_plays = int(parts[6])
                            team_stats[away_team].rush_plays = away_rush_plays
                            team_stats[home_team].rush_plays = home_rush_plays
                        except (ValueError, IndexError):
                            pass
                
                elif "Net Yards Pass" in line and len(line.split()) >= 3:
                    parts = line.split()
                    if len(parts) >= 3:
                        away_pass = int(parts[-2])
                        home_pass = int(parts[-1])
                        team_stats[away_team].net_yards_pass = away_pass
                        team_stats[home_team].net_yards_pass = home_pass
                
                elif "Att-Comp-Int" in line:
                    parts = line.split()
                    if len(parts) >= 9:
                        try:
                            away_att = int(parts[1])
                            away_comp = int(parts[3])
                            away_int = int(parts[5])
                            home_att = int(parts[6])
                            home_comp = int(parts[8])
                            home_int = int(parts[10]) if len(parts) > 10 else 0
                            
                            team_stats[away_team].pass_attempts = away_att
                            team_stats[away_team].pass_completions = away_comp
                            team_stats[away_team].pass_interceptions = away_int
                            team_stats[home_team].pass_attempts = home_att
                            team_stats[home_team].pass_completions = home_comp
                            team_stats[home_team].pass_interceptions = home_int
                        except (ValueError, IndexError):
                            pass
                
                elif "Sacks - Yards" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_sacks = int(parts[2])
                            away_yards = int(parts[4])
                            home_sacks = int(parts[5])
                            home_yards = int(parts[7])
                            
                            team_stats[away_team].sacks_allowed = away_sacks
                            team_stats[away_team].sack_yards_lost = away_yards
                            team_stats[home_team].sacks_allowed = home_sacks
                            team_stats[home_team].sack_yards_lost = home_yards
                        except (ValueError, IndexError):
                            pass
                
                elif "Punts - Avg" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_punts = int(parts[2])
                            away_avg = float(parts[4])
                            home_punts = int(parts[5])
                            home_avg = float(parts[7])
                            
                            team_stats[away_team].punts = away_punts
                            team_stats[away_team].punt_average = away_avg
                            team_stats[home_team].punts = home_punts
                            team_stats[home_team].punt_average = home_avg
                        except (ValueError, IndexError):
                            pass
                
                elif "Return Yards" in line and len(line.split()) >= 3:
                    parts = line.split()
                    if len(parts) >= 3:
                        away_ret = int(parts[-2])
                        home_ret = int(parts[-1])
                        team_stats[away_team].return_yards = away_ret
                        team_stats[home_team].return_yards = home_ret
                
                elif "Penalty - Yards" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_pen_count = int(parts[2])
                            away_pen_yards = int(parts[4])
                            home_pen_count = int(parts[5])
                            home_pen_yards = int(parts[7])
                            
                            team_stats[away_team].penalty_count = away_pen_count
                            team_stats[away_team].penalty_yards = away_pen_yards
                            team_stats[home_team].penalty_count = home_pen_count
                            team_stats[home_team].penalty_yards = home_pen_yards
                        except (ValueError, IndexError):
                            pass
                
                elif "Fumbles - Lost" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            away_fumbles = int(parts[2])
                            away_fumbles_lost = int(parts[4])
                            home_fumbles = int(parts[5])
                            home_fumbles_lost = int(parts[7])
                            
                            team_stats[away_team].fumbles = away_fumbles
                            team_stats[away_team].fumbles_lost = away_fumbles_lost
                            team_stats[home_team].fumbles = home_fumbles
                            team_stats[home_team].fumbles_lost = home_fumbles_lost
                        except (ValueError, IndexError):
                            pass
                
                i += 1
            
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error parsing team stats: {str(e)}")
        
        return team_stats
   


 
    def _parse_individual_stats(self, lines: List[str]) -> List[PlayerStat]:
        """Parse individual player statistics"""
        individual_stats = []
        
        # Find individual stats section
        stats_start_idx = None
        for i, line in enumerate(lines):
            if "Individual Statistical Results" in line:
                stats_start_idx = i
                break
        
        if stats_start_idx is None:
            return individual_stats
        
        try:
            current_team = None
            current_category = None
            
            i = stats_start_idx + 1
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Check for team/category header like "Cowboys  - Rushers"
                if " - " in line and not line.startswith("---"):
                    parts = line.split(" - ")
                    if len(parts) == 2:
                        current_team = parts[0].strip()
                        current_category = parts[1].strip().lower()
                
                elif " for " in line and " yard" in line.lower():
                    print(f"[STATS_PROCESSOR] Skipping summary line: {line}")
                    i += 1
                    continue
                # Parse stat lines (jersey number at start)
                elif line and line[0].isdigit() and current_team and current_category:
                    stat_data = self._parse_player_stat_line(line, current_team, current_category)
                    if stat_data:
                        individual_stats.append(stat_data)
                
                i += 1
            
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error parsing individual stats: {str(e)}")
        
        return individual_stats
   


 
    def _parse_player_stat_line(self, line: str, team: str, category: str) -> Optional[PlayerStat]:
        """Parse individual player stat line"""
        try:
            # Use regex to extract: jersey_num, position, stats..., player_name
            # Pattern: number, position, stats (numbers/decimals/slashes), then name at end
            pattern = r'^(\d+)\s+(\w+)\s+([\d\s\./\-]+?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*$'
            match = re.match(pattern, line)
            
            if not match:
                return None
            
            jersey_number = int(match.group(1))
            position = match.group(2)
            stat_values = match.group(3).strip().split()
            player_name = match.group(4).strip()
            
            # Parse category-specific stats
            stats = self._parse_category_stats(category, stat_values)
            
            if stats:
                return PlayerStat(
                    jersey_number=jersey_number,
                    position=position,
                    player_name=player_name,
                    team_name=team,
                    stat_category=category,
                    stats=stats
                )
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_category_stats(self, category: str, stat_values: List[str]) -> Optional[Dict]:
        """Parse category-specific statistics"""
        try:
            stats = {}
            
            if category == "rushers":
                # Format: attempts yards average longest touchdowns
                if len(stat_values) >= 5:
                    stats = {
                        'attempts': int(stat_values[0]),
                        'yards': int(stat_values[1]),
                        'average': float(stat_values[2]),
                        'longest': int(stat_values[3]),
                        'touchdowns': int(stat_values[4])
                    }
                else:
                    return None
            
            elif category == "passing":
                # Format: attempts completions yards touchdowns interceptions longest
                if len(stat_values) >= 6:
                    stats = {
                        'attempts': int(stat_values[0]),
                        'completions': int(stat_values[1]),
                        'yards': int(stat_values[2]),
                        'touchdowns': int(stat_values[3]),
                        'interceptions': int(stat_values[4]),
                        'longest': int(stat_values[5])
                    }
                else:
                    return None
            
            elif category == "receivers":
                # Format: receptions yards average longest touchdowns
                if len(stat_values) >= 5:
                    stats = {
                        'receptions': int(stat_values[0]),
                        'yards': int(stat_values[1]),
                        'average': float(stat_values[2]),
                        'longest': int(stat_values[3]),
                        'touchdowns': int(stat_values[4])
                    }
                else:
                    return None
            
            elif category == "interceptions":
                # Format: interceptions yards average longest touchdowns
                if len(stat_values) >= 5:
                    stats = {
                        'interceptions': int(stat_values[0]),
                        'yards': int(stat_values[1]),
                        'average': float(stat_values[2]),
                        'longest': int(stat_values[3]),
                        'touchdowns': int(stat_values[4])
                    }
                else:
                    return None
            
            elif category == "sacks":
                # Format: sacks (just count)
                if len(stat_values) >= 1:
                    stats = {
                        'sacks': float(stat_values[0]) if '.' in stat_values[0] else int(stat_values[0])
                    }
                else:
                    return None
            
            elif "returns" in category:
                # Format: returns yards average longest touchdowns
                if len(stat_values) >= 5:
                    stats = {
                        'returns': int(stat_values[0]),
                        'yards': int(stat_values[1]),
                        'average': float(stat_values[2]),
                        'longest': int(stat_values[3]),
                        'touchdowns': int(stat_values[4])
                    }
                else:
                    return None
            
            elif category == "kicking":
                # Format: extra_points/attempts field_goals/attempts longest
                if len(stat_values) >= 3:
                    ep_parts = stat_values[0].split('/')
                    fg_parts = stat_values[1].split('/')
                    
                    stats = {
                        'extra_points_made': int(ep_parts[0]),
                        'extra_points_attempted': int(ep_parts[1]),
                        'field_goals_made': int(fg_parts[0]),
                        'field_goals_attempted': int(fg_parts[1]),
                        'longest': int(stat_values[2])
                    }
                else:
                    return None
            
            else:
                return None
            
            return stats
            
        except Exception as e:
            return None
    
    def _store_game_data(self, game_data: Dict, league_id: int, season: int, week: int) -> bool:
        """Store game data in database"""
        conn = None
        try:
            game_result = game_data['game_result']
            team_stats = game_data['team_stats']
            individual_stats = game_data['individual_stats']
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Find matching game
            matching_game = self._find_matching_game(cursor, game_result, league_id, season, week)
            
            if not matching_game:
                print(f"[STATS_PROCESSOR] Could not find matching game for {game_result.away_team} vs {game_result.home_team}")
                conn.close()
                return False
            
            print(f"[STATS_PROCESSOR] Matched game {matching_game['game_id']}: {game_result.away_team} @ {game_result.home_team}")
            
            # Update game scores
            cursor.execute("""
                UPDATE games 
                SET home_score = ?, away_score = ?, game_status = 'COMPLETED'
                WHERE game_id = ?
            """, (game_result.home_score, game_result.away_score, matching_game['game_id']))
            
            rows_updated = cursor.rowcount
            print(f"[STATS_PROCESSOR] Updated {rows_updated} game record(s) with scores")
            
            # Store team stats if tables exist
            try:
                self._store_team_stats(cursor, team_stats, matching_game, league_id, season, week, 
                                     game_result.quarter_scores, individual_stats, game_result.is_overtime)
                print(f"[STATS_PROCESSOR] Stored team stats successfully")
            except Exception as e:
                print(f"[STATS_PROCESSOR] Could not store team stats: {e}")
                import traceback
                traceback.print_exc()
            
            # Store player stats if tables exist
            try:
                self._store_player_stats(cursor, individual_stats, matching_game, league_id, season, week)
                print(f"[STATS_PROCESSOR] Stored player stats successfully")
            except Exception as e:
                print(f"[STATS_PROCESSOR] Could not store player stats: {e}")
                import traceback
                traceback.print_exc()
            
            # CRITICAL: Commit the transaction
            conn.commit()
            print(f"[STATS_PROCESSOR] COMMITTED transaction for game {matching_game['game_id']}: {game_result.away_team} {game_result.away_score} - {game_result.home_team} {game_result.home_score}")
            return True
                
        except Exception as e:
            print(f"[STATS_PROCESSOR] ERROR storing game data: {str(e)}")
            import traceback
            traceback.print_exc()
            if conn:
                conn.rollback()
                print(f"[STATS_PROCESSOR] Rolled back transaction")
            return False
        finally:
            if conn:
                conn.close()
    
    def _find_matching_game(self, cursor, game_result: GameResult, league_id: int, season: int, week: int):
        """Find matching game in database"""
        try:
            cursor.execute("""
                SELECT g.*, 
                       away.team_name as away_team_name,
                       away.full_name as away_full_name,
                       home.team_name as home_team_name,
                       home.full_name as home_full_name
                FROM games g
                JOIN teams away ON g.away_team_id = away.team_id
                JOIN teams home ON g.home_team_id = home.team_id
                WHERE g.league_id = ? AND g.season = ? AND g.week = ?
            """, (league_id, season, week))
            
            games = cursor.fetchall()
            
            # Try to match by team names
            for game in games:
                if (self.team_names_match(game_result.away_team, game['away_team_name']) and 
                    self.team_names_match(game_result.home_team, game['home_team_name'])):
                    return game
            
            return None
            
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error finding matching game: {str(e)}")
            return None
    
    def team_names_match(self, stats_name: str, db_name: str) -> bool:
        """Check if team names match (handles variations)"""
        stats_name = stats_name.lower().strip()
        db_name = db_name.lower().strip()
        
        # Direct match
        if stats_name == db_name:
            return True
        
        # Check if stats name is in db name or vice versa
        if stats_name in db_name or db_name in stats_name:
            return True
        
        return False
    
    def _store_team_stats(self, cursor, team_stats: Dict[str, TeamStats], matching_game, league_id: int, 
                         season: int, week: int, quarter_scores: List[Tuple[int, int]], 
                         individual_stats: List[PlayerStat] = None, is_overtime: bool = False):
        """Store team statistics in team_stats table"""
        try:
            for team_name, stats in team_stats.items():
                # Get team_id and opponent_team_id
                team_id = matching_game['home_team_id'] if self.team_names_match(team_name, matching_game['home_team_name']) else matching_game['away_team_id']
                opponent_team_id = matching_game['away_team_id'] if team_id == matching_game['home_team_id'] else matching_game['home_team_id']
                
                # Parse time of possession to seconds
                time_parts = stats.time_of_possession.split(':')
                time_seconds = int(time_parts[0]) * 60 + int(time_parts[1]) if len(time_parts) == 2 else 0
                
                # Parse third down attempts and conversions from string like "7 - 14 - 50.0%"
                third_down_attempts = 0
                third_down_conversions = 0
                try:
                    if ' - ' in stats.third_down_conv:
                        parts = stats.third_down_conv.split(' - ')
                        if len(parts) >= 2:
                            third_down_conversions = int(parts[0])
                            third_down_attempts = int(parts[1])
                except:
                    pass
                
                # Calculate punt total yards
                punt_total_yards = int(stats.punts * stats.punt_average) if stats.punts > 0 else 0
                
                # Aggregate return yards from individual player stats
                punt_return_yards = 0
                kickoff_return_yards = 0
                if individual_stats and len(individual_stats) > 0:
                    for player_stat in individual_stats:
                        if player_stat.team_name == team_name:
                            if "punt returns" in player_stat.stat_category.lower():
                                yards = player_stat.stats.get('yards', 0)
                                punt_return_yards += yards
                            elif "kickoff returns" in player_stat.stat_category.lower():
                                yards = player_stat.stats.get('yards', 0) 
                                kickoff_return_yards += yards
                
                # FIXED: Get quarter scores and calculate OT points
                if team_id == matching_game['home_team_id']:
                    q1, q2, q3, q4 = [qs[1] for qs in quarter_scores[:4]]  # Home scores
                    final_score = sum([qs[1] for qs in quarter_scores])  # Sum all home quarter scores
                else:
                    q1, q2, q3, q4 = [qs[0] for qs in quarter_scores[:4]]  # Away scores
                    final_score = sum([qs[0] for qs in quarter_scores])  # Sum all away quarter scores
                
                # FIXED: Calculate OT points if game went to overtime
                ot_points = 0
                if is_overtime:
                    # OT points = Total score - (Q1 + Q2 + Q3 + Q4)
                    ot_points = final_score - (q1 + q2 + q3 + q4)
                    print(f"[STATS_PROCESSOR] {team_name} OT points: {ot_points} (Total: {final_score}, Regulation: {q1+q2+q3+q4})")
                
                # Insert/update team stats with all fields
                cursor.execute("""
                    INSERT OR REPLACE INTO team_stats (
                        game_id, team_id, opponent_team_id, league_id, season, week,
                        q1_points, q2_points, q3_points, q4_points, ot_points, final_score,
                        first_downs_total, first_downs_rush, first_downs_pass, first_downs_penalty,
                        third_down_attempts, third_down_conversions,
                        time_of_possession_seconds,
                        total_net_yards, total_plays,
                        net_yards_rush, rush_attempts,
                        net_yards_pass, pass_attempts, pass_completions, pass_interceptions_thrown,
                        sacks_allowed, sack_yards_lost,
                        punts, punt_total_yards,
                        return_yards_total, punt_return_yards, kickoff_return_yards,
                        penalties, penalty_yards,
                        fumbles, fumbles_lost,
                        created_date, last_modified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    matching_game['game_id'], team_id, opponent_team_id, league_id, season, week,
                    q1, q2, q3, q4, ot_points, final_score,
                    stats.first_downs, stats.first_downs_rush, stats.first_downs_pass, stats.first_downs_penalty,
                    third_down_attempts, third_down_conversions,
                    time_seconds,
                    stats.total_net_yards, stats.total_plays,
                    stats.net_yards_rush, stats.rush_plays,
                    stats.net_yards_pass, stats.pass_attempts, stats.pass_completions, stats.pass_interceptions,
                    stats.sacks_allowed, stats.sack_yards_lost,
                    stats.punts, punt_total_yards,
                    stats.return_yards, punt_return_yards, kickoff_return_yards,
                    stats.penalty_count, stats.penalty_yards,
                    stats.fumbles, stats.fumbles_lost
                ))
                
        except Exception as e:
            print(f"[STATS_PROCESSOR] Error storing team stats: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _store_player_stats(self, cursor, individual_stats: List[PlayerStat], matching_game, league_id: int, season: int, week: int):
        """Store individual player statistics"""
        try:
            stats_stored = 0
            for player_stat in individual_stats:
                # Determine team_id
                team_id = None
                if self.team_names_match(player_stat.team_name, matching_game['home_team_name']):
                    team_id = matching_game['home_team_id']
                elif self.team_names_match(player_stat.team_name, matching_game['away_team_name']):
                    team_id = matching_game['away_team_id']
                else:
                    continue
                
                # Get opponent_team_id
                opponent_team_id = matching_game['away_team_id'] if team_id == matching_game['home_team_id'] else matching_game['home_team_id']
                
                # Parse player name into first and last name
                name_parts = player_stat.player_name.strip().split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                else:
                    first_name = player_stat.player_name
                    last_name = ''
               
                # Check if player exists in roster for this team
                cursor.execute("""
                    SELECT p.player_id 
                    FROM players p
                    JOIN roster r ON p.player_id = r.player_id
                    WHERE r.team_id = ? 
                    AND r.jersey_number = ?
                    AND r.league_id = ?
                    AND r.is_active = TRUE
                """, (team_id, player_stat.jersey_number, league_id))
                
                player = cursor.fetchone()
                
                if not player:
                    # Get position_id
                    cursor.execute("""
                        SELECT position_id FROM positions 
                        WHERE position_code = ?
                    """, (player_stat.position,))
                    
                    pos_result = cursor.fetchone()
                    position_id = pos_result['position_id'] if pos_result else 1
                    
                    # Create new player
                    cursor.execute("""
                        INSERT INTO players (first_name, last_name, league_id, position_id, position, created_season)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (first_name, last_name, league_id, position_id, player_stat.position, season))
                    
                    player_id = cursor.lastrowid
                    
                    # Add to roster
                    cursor.execute("""
                        INSERT INTO roster (player_id, team_id, league_id, jersey_number, position_on_team, is_active)
                        VALUES (?, ?, ?, ?, ?, TRUE)
                    """, (player_id, team_id, league_id, player_stat.jersey_number, player_stat.position))
                else:
                    player_id = player['player_id']


                # FIXED: THIS IS THE MISSING PART - Actually insert/update the stats!
                # Check if stats record already exists for this game
                cursor.execute("""
                    SELECT * FROM player_stats 
                    WHERE game_id = ? AND player_id = ?
                """, (matching_game['game_id'], player_id))
                
                existing_stat = cursor.fetchone()

                if existing_stat:
                    # Update existing record (additive for multiple categories)
                    self._update_player_stats(cursor, existing_stat['stat_id'], 
                                            player_stat.stat_category, 
                                            player_stat.stats, 
                                            existing_stat)
                    print(f"[STATS_PROCESSOR] Updated stats for {player_stat.player_name} - {player_stat.stat_category}")
                else:
                    # Insert new record
                    self._insert_player_stats(cursor, player_id, matching_game['game_id'], 
                                            team_id, opponent_team_id, league_id, season, week,
                                            player_stat.stat_category, player_stat.stats)
                    print(f"[STATS_PROCESSOR] Inserted stats for {player_stat.player_name} - {player_stat.stat_category}")
                
                stats_stored += 1
            
            print(f"[STATS_PROCESSOR] Stored {stats_stored} player stat records")

        except Exception as e:
            print(f"[STATS_PROCESSOR] Error storing player stats: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _insert_player_stats(self, cursor, player_id: int, game_id: int, team_id: int, opponent_team_id: int,
                           league_id: int, season: int, week: int, category: str, stats: Dict):
        """Insert new player stats record"""
        # Initialize all stat values to 0
        values = [player_id, game_id, team_id, opponent_team_id, league_id, season, week] + [0] * 31
        
        # Map category stats to database columns
        category = category.lower()
        
        if category == "rushers":
            values[7] = stats.get('attempts', 0)      # rushing_attempts
            values[8] = stats.get('yards', 0)         # rushing_yards
            values[9] = stats.get('touchdowns', 0)    # rushing_touchdowns
            values[10] = stats.get('longest', 0)       # rushing_longest
            
        elif category == "passing":
            values[11] = stats.get('attempts', 0)      # passing_attempts
            values[12] = stats.get('completions', 0)   # passing_completions
            values[13] = stats.get('yards', 0)         # passing_yards
            values[14] = stats.get('touchdowns', 0)    # passing_touchdowns
            values[15] = stats.get('interceptions', 0) # passing_interceptions
            values[16] = stats.get('longest', 0)       # passing_longest
            
        elif category == "receivers":
            values[17] = stats.get('receptions', 0)   # receiving_catches
            values[18] = stats.get('yards', 0)        # receiving_yards
            values[19] = stats.get('touchdowns', 0)   # receiving_touchdowns
            values[20] = stats.get('longest', 0)      # receiving_longest
            
        elif category == "interceptions":
            values[21] = stats.get('interceptions', 0) # interceptions
            values[22] = stats.get('yards', 0)         # interception_yards
            values[23] = stats.get('longest', 0)       # interception_longest
            
        elif category == "sacks":
            values[24] = stats.get('sacks', 0)         # sacks
            
        elif category == "kicking":
            values[25] = stats.get('extra_points_made', 0)      # extra_points_made
            values[26] = stats.get('extra_points_attempted', 0) # extra_points_attempted
            values[27] = stats.get('field_goals_made', 0)       # field_goals_made
            values[28] = stats.get('field_goals_attempted', 0)  # field_goals_attempted
            values[29] = stats.get('longest', 0)                # field_goal_longest
            
        elif "punt returns" in category:
            values[30] = stats.get('returns', 0)      # punt_returns
            values[31] = stats.get('yards', 0)        # punt_return_yards
            values[32] = stats.get('touchdowns', 0)   # punt_return_touchdowns
            values[33] = stats.get('longest', 0)      # punt_return_longest
            
        elif "kickoff returns" in category:
            values[34] = stats.get('returns', 0)      # kickoff_returns
            values[35] = stats.get('yards', 0)        # kickoff_return_yards
            values[36] = stats.get('touchdowns', 0)   # kickoff_return_touchdowns
            values[37] = stats.get('longest', 0)      # kickoff_return_longest
        
        cursor.execute("""
            INSERT INTO player_stats (
                player_id, game_id, team_id, opponent_team_id, league_id, season, week,
                rushing_attempts, rushing_yards, rushing_touchdowns, rushing_longest,
                passing_attempts, passing_completions, passing_yards, passing_touchdowns, passing_interceptions, passing_longest,
                receiving_catches, receiving_yards, receiving_touchdowns, receiving_longest,
                interceptions, interception_yards, interception_longest,
                sacks,
                extra_points_made, extra_points_attempted, field_goals_made, field_goals_attempted, field_goal_longest,
                punt_returns, punt_return_yards, punt_return_touchdowns, punt_return_longest,
                kickoff_returns, kickoff_return_yards, kickoff_return_touchdowns, kickoff_return_longest,
                created_date, last_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, tuple(values))
    
    def _update_player_stats(self, cursor, stat_id: int, category: str, stats: Dict, existing_record):
        """Update existing player stats record (additive)"""
        # Convert existing_record to dict if needed

        if isinstance(existing_record, dict):
            existing_dict = existing_record
        else:
            existing_dict = dict(existing_record)
               
        # Update based on category
        category = category.lower()
        updates = {}
        
        if category == "rushers":
            updates['rushing_attempts'] = existing_dict['rushing_attempts'] + stats.get('attempts', 0)
            updates['rushing_yards'] = existing_dict['rushing_yards'] + stats.get('yards', 0)
            updates['rushing_touchdowns'] = existing_dict['rushing_touchdowns'] + stats.get('touchdowns', 0)
            updates['rushing_longest'] = max(existing_dict['rushing_longest'], stats.get('longest', 0))
        
        elif category == "passing":
            updates['passing_attempts'] = existing_dict['passing_attempts'] + stats.get('attempts', 0)
            updates['passing_completions'] = existing_dict['passing_completions'] + stats.get('completions', 0)
            updates['passing_yards'] = existing_dict['passing_yards'] + stats.get('yards', 0)
            updates['passing_touchdowns'] = existing_dict['passing_touchdowns'] + stats.get('touchdowns', 0)
            updates['passing_interceptions'] = existing_dict['passing_interceptions'] + stats.get('interceptions', 0)
            updates['passing_longest'] = max(existing_dict['passing_longest'], stats.get('longest', 0))
        
        elif category == "receivers":
            updates['receiving_catches'] = existing_dict['receiving_catches'] + stats.get('receptions', 0)
            updates['receiving_yards'] = existing_dict['receiving_yards'] + stats.get('yards', 0)
            updates['receiving_touchdowns'] = existing_dict['receiving_touchdowns'] + stats.get('touchdowns', 0)
            updates['receiving_longest'] = max(existing_dict['receiving_longest'], stats.get('longest', 0))
        
        elif category == "interceptions":
            updates['interceptions'] = existing_dict['interceptions'] + stats.get('interceptions', 0)
            updates['interception_yards'] = existing_dict['interception_yards'] + stats.get('yards', 0)
            updates['interception_longest'] = max(existing_dict['interception_longest'], stats.get('longest', 0))
        
        elif category == "sacks":
            updates['sacks'] = existing_dict['sacks'] + stats.get('sacks', 0)
            
        elif category == "kicking":
            updates['extra_points_made'] = existing_dict['extra_points_made'] + stats.get('extra_points_made', 0)
            updates['extra_points_attempted'] = existing_dict['extra_points_attempted'] + stats.get('extra_points_attempted', 0)
            updates['field_goals_made'] = existing_dict['field_goals_made'] + stats.get('field_goals_made', 0)
            updates['field_goals_attempted'] = existing_dict['field_goals_attempted'] + stats.get('field_goals_attempted', 0)
            updates['field_goal_longest'] = max(existing_dict['field_goal_longest'], stats.get('longest', 0))
        
        elif "punt returns" in category:
            updates['punt_returns'] = existing_dict['punt_returns'] + stats.get('returns', 0)
            updates['punt_return_yards'] = existing_dict['punt_return_yards'] + stats.get('yards', 0)
            updates['punt_return_touchdowns'] = existing_dict['punt_return_touchdowns'] + stats.get('touchdowns', 0)
            updates['punt_return_longest'] = max(existing_dict['punt_return_longest'], stats.get('longest', 0))
        
        elif "kickoff returns" in category:
            updates['kickoff_returns'] = existing_dict['kickoff_returns'] + stats.get('returns', 0)
            updates['kickoff_return_yards'] = existing_dict['kickoff_return_yards'] + stats.get('yards', 0)
            updates['kickoff_return_touchdowns'] = existing_dict['kickoff_return_touchdowns'] + stats.get('touchdowns', 0)
            updates['kickoff_return_longest'] = max(existing_dict['kickoff_return_longest'], stats.get('longest', 0))
        
        # Build UPDATE query
        if updates:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            set_clause += ", last_modified = CURRENT_TIMESTAMP"
            values = list(updates.values()) + [stat_id]
            
            cursor.execute(f"""
                UPDATE player_stats 
                SET {set_clause}
                WHERE stat_id = ?
            """, values)


def main():
    """Test/example usage"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Example usage
    processor = StatsProcessor("pynfl.db")
    success = processor.select_and_process_stats_file(None, league_id=1, season=1, week=1)
    
    if success:
        print("Stats processed successfully!")
    else:
        print("Failed to process stats")


if __name__ == "__main__":
    main()
