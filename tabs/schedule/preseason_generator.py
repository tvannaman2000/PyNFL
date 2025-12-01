# ========================================
# schedule/preseason_generator.py
# ========================================

"""
Preseason Schedule Generation Module

Handles generation of preseason schedules based on league configuration.
Preseason games are typically exhibition games between teams from different
divisions/conferences to prepare for the regular season.

Rules:
- Teams cannot play opponents from their own division
- Teams cannot play the same opponent more than once
- Each team plays exactly once per week
- Every team plays each week
- Every team gets at least 1 home game and 1 away game
"""

import sqlite3
from typing import List, Dict, Tuple, Optional, Set
import random


class PreseasonGenerator:
    """Handles preseason schedule generation"""
    
    def __init__(self, db_path: str):
        print(f"[PRESEASON_GEN] Initializing with db_path: {db_path}")
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_schedule(self, league_id: int, season: int) -> bool:
        """
        Generate preseason schedule for the specified league and season
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[PRESEASON_GEN] ✓ METHOD CALLED: league_id={league_id}, season={season}")
        
        try:
            # Step 1: Get league preseason settings
            print(f"[PRESEASON_GEN] Step 1: Getting preseason settings...")
            preseason_weeks = self._get_preseason_settings(league_id)
            print(f"[PRESEASON_GEN] Got {preseason_weeks} preseason weeks")
            
            if not preseason_weeks:
                print("No preseason games configured")
                return True
            
            # Step 2: Get teams organized by division
            print(f"[PRESEASON_GEN] Step 2: Getting teams by division...")
            teams_by_division = self._get_teams_by_division(league_id)
            all_teams = []
            for division_id, division_teams in teams_by_division.items():
                all_teams.extend(division_teams)
                print(f"[PRESEASON_GEN] Division {division_id}: {len(division_teams)} teams")
            
            total_teams = len(all_teams)
            print(f"[PRESEASON_GEN] Total teams: {total_teams}")
            
            if total_teams < 2:
                raise ValueError("Need at least 2 teams to generate preseason schedule")
            
            if total_teams % 2 != 0:
                raise ValueError("Need even number of teams for weekly matchups")
            
            # Step 3: Validate that schedule is possible
            print(f"[PRESEASON_GEN] Step 3: Validating schedule...")
            if not self._validate_schedule_possible(teams_by_division, preseason_weeks):
                print(f"[PRESEASON_GEN] ✗ Schedule validation failed")
                return False
            print(f"[PRESEASON_GEN] ✓ Schedule validation passed")
            
            # Step 4: Generate weekly matchups with home/away balancing
            print(f"[PRESEASON_GEN] Step 4: Generating balanced weekly matchups...")
            weekly_matchups = self._generate_balanced_weekly_matchups(teams_by_division, preseason_weeks)
            print(f"[PRESEASON_GEN] Generated {len(weekly_matchups)} weeks of matchups")
            
            # Step 5: Validate home/away balance
            print(f"[PRESEASON_GEN] Step 5: Validating home/away balance...")
            self._validate_home_away_balance(weekly_matchups, all_teams)
            
            # Step 6: Convert to scheduled games and insert into database
            print(f"[PRESEASON_GEN] Step 6: Creating scheduled games...")
            scheduled_games = self._create_scheduled_games(weekly_matchups)
            print(f"[PRESEASON_GEN] Created {len(scheduled_games)} scheduled games")
            
            print(f"[PRESEASON_GEN] Step 7: Inserting games into database...")
            self._insert_preseason_games(league_id, season, scheduled_games)
            print(f"[PRESEASON_GEN] ✓ Database insertion complete")
            
            print(f"[PRESEASON_GEN] ✓ SUCCESS: Generated {len(scheduled_games)} preseason games for season {season}")
            return True
            
        except Exception as e:
            print(f"[PRESEASON_GEN] ✗ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return False 

    def clear_preseason_games(self, league_id: int, season: int) -> bool:
        """
        Clear all preseason games for the specified league and season
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            True if successful, False otherwise
        """
        print(f"[PRESEASON_GEN] ✓ CLEAR METHOD CALLED: league_id={league_id}, season={season}")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, check how many preseason games exist
                cursor.execute("""
                    SELECT COUNT(*) as game_count
                    FROM games 
                    WHERE league_id = ? AND season = ? AND game_type = 'PRESEASON'
                """, (league_id, season))
                
                result = cursor.fetchone()
                games_to_delete = result['game_count'] if result else 0
                print(f"[PRESEASON_GEN] Found {games_to_delete} preseason games to delete")
                
                if games_to_delete == 0:
                    print(f"[PRESEASON_GEN] No preseason games found for season {season}")
                    return True  # Nothing to delete is considered success
                
                # Delete all preseason games for this league and season
                cursor.execute("""
                    DELETE FROM games 
                    WHERE league_id = ? AND season = ? AND game_type = 'PRESEASON'
                """, (league_id, season))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"[PRESEASON_GEN] ✓ Successfully deleted {deleted_count} preseason games")
                return True
                
        except Exception as e:
            print(f"[PRESEASON_GEN] ✗ EXCEPTION during clear: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _get_preseason_settings(self, league_id: int) -> int:
        """Get number of preseason weeks from league settings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preseason_games 
                FROM leagues 
                WHERE league_id = ? AND is_active = TRUE
            """, (league_id,))
            
            result = cursor.fetchone()
            return result['preseason_games'] if result else 0
    
    def _get_teams_by_division(self, league_id: int) -> Dict[int, List[Dict]]:
        """Get teams organized by division"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT team_id, team_name, division_id, conference_id
                FROM teams 
                WHERE league_id = ? AND is_active = TRUE
                ORDER BY division_id, team_name
            """, (league_id,))
            
            teams = cursor.fetchall()
            
            teams_by_division = {}
            for team in teams:
                team_dict = dict(team)
                division_id = team['division_id']
                
                if division_id not in teams_by_division:
                    teams_by_division[division_id] = []
                teams_by_division[division_id].append(team_dict)
            
            return teams_by_division
    
    def _validate_schedule_possible(self, teams_by_division: Dict[int, List[Dict]], weeks: int) -> bool:
        """Validate that the schedule is mathematically possible"""
        
        # Count total teams and teams per division
        all_teams = []
        for division_teams in teams_by_division.values():
            all_teams.extend(division_teams)
        
        total_teams = len(all_teams)
        
        # Each team needs to play 'weeks' games
        # Each team can only play non-division opponents
        for division_id, division_teams in teams_by_division.items():
            teams_in_division = len(division_teams)
            non_division_teams = total_teams - teams_in_division
            
            if non_division_teams < weeks:
                print(f"Division {division_id} has {teams_in_division} teams, "
                      f"but only {non_division_teams} non-division opponents available "
                      f"for {weeks} preseason weeks")
                return False
        
        return True
    
    def _generate_balanced_weekly_matchups(self, teams_by_division: Dict[int, List[Dict]], weeks: int) -> List[List[Tuple[int, int]]]:
        """
        Generate matchups for each week ensuring all constraints are met AND home/away balance
        
        Returns:
            List of weekly matchups, where each week is a list of (away_team_id, home_team_id) tuples
        """
        
        # Get all teams in a flat list
        all_teams = []
        team_to_division = {}
        for division_id, division_teams in teams_by_division.items():
            for team in division_teams:
                all_teams.append(team)
                team_to_division[team['team_id']] = division_id
        
        # Track which teams have played each other
        played_matchups: Set[Tuple[int, int]] = set()
        
        # Track home/away counts for each team
        home_counts = {team['team_id']: 0 for team in all_teams}
        away_counts = {team['team_id']: 0 for team in all_teams}
        
        weekly_matchups = []
        
        # Generate matchups for each week
        for week in range(1, weeks + 1):
            print(f"[PRESEASON_GEN] Generating week {week} matchups...")
            
            week_matchups = self._generate_balanced_week_matchups(
                all_teams, team_to_division, played_matchups, home_counts, away_counts, week, weeks
            )
            
            if not week_matchups:
                raise ValueError(f"Could not generate valid matchups for week {week}")
            
            weekly_matchups.append(week_matchups)
            
            # Update played matchups and home/away counts
            for away_id, home_id in week_matchups:
                played_matchups.add((away_id, home_id))
                played_matchups.add((home_id, away_id))  # Both directions
                away_counts[away_id] += 1
                home_counts[home_id] += 1
            
            # Debug: Print current home/away balance
            print(f"[PRESEASON_GEN] Week {week} home/away counts:")
            for team in all_teams[:4]:  # Show first 4 teams as example
                team_id = team['team_id']
                team_name = team['team_name']
                print(f"  {team_name}: {home_counts[team_id]}H, {away_counts[team_id]}A")
        
        return weekly_matchups
    
    def _generate_balanced_week_matchups(self, all_teams: List[Dict], team_to_division: Dict[int, int], 
                                       played_matchups: Set[Tuple[int, int]], home_counts: Dict[int, int],
                                       away_counts: Dict[int, int], current_week: int, total_weeks: int) -> List[Tuple[int, int]]:
        """
        Generate valid matchups for a single week with home/away balancing
        """
        
        team_ids = [team['team_id'] for team in all_teams]
        random.shuffle(team_ids)  # Randomize for variety
        
        def can_play(team1_id: int, team2_id: int) -> bool:
            """Check if two teams can play each other"""
            # Same division?
            if team_to_division[team1_id] == team_to_division[team2_id]:
                return False
            
            # Already played?
            if (team1_id, team2_id) in played_matchups or (team2_id, team1_id) in played_matchups:
                return False
            
            return True
        
        def choose_home_away(team1_id: int, team2_id: int) -> Tuple[int, int]:
            """Choose which team should be home vs away based on current balance"""
            team1_home = home_counts[team1_id]
            team1_away = away_counts[team1_id]
            team2_home = home_counts[team2_id]
            team2_away = away_counts[team2_id]
            
            # Calculate how many more games each team will play after this one
            remaining_games = total_weeks - current_week
            
            # Priority 1: If a team has no home games and this is getting late in preseason
            if team1_home == 0 and remaining_games <= 1:
                return (team2_id, team1_id)  # team1 gets home game
            if team2_home == 0 and remaining_games <= 1:
                return (team1_id, team2_id)  # team2 gets home game
                
            # Priority 2: If a team has no away games and this is getting late in preseason
            if team1_away == 0 and remaining_games <= 1:
                return (team1_id, team2_id)  # team1 gets away game
            if team2_away == 0 and remaining_games <= 1:
                return (team2_id, team1_id)  # team2 gets away game
            
            # Priority 3: Balance home games - prefer team with fewer home games to get home game
            if team1_home < team2_home:
                return (team2_id, team1_id)  # team1 gets home game
            elif team2_home < team1_home:
                return (team1_id, team2_id)  # team2 gets home game
            
            # Priority 4: Balance away games - prefer team with fewer away games to get away game
            elif team1_away < team2_away:
                return (team1_id, team2_id)  # team1 gets away game
            elif team2_away < team1_away:
                return (team2_id, team1_id)  # team2 gets away game
            
            # If everything is equal, randomize
            else:
                if random.choice([True, False]):
                    return (team1_id, team2_id)  # team1 away, team2 home
                else:
                    return (team2_id, team1_id)  # team2 away, team1 home
        
        def find_matchups(remaining_teams: List[int]) -> List[Tuple[int, int]]:
            """Recursively find valid matchups using backtracking"""
            if not remaining_teams:
                return []
            
            if len(remaining_teams) % 2 != 0:
                return None  # Can't pair odd number of teams
            
            # Try to pair the first team with each possible opponent
            first_team = remaining_teams[0]
            
            for i in range(1, len(remaining_teams)):
                potential_opponent = remaining_teams[i]
                
                if can_play(first_team, potential_opponent):
                    # Try this pairing
                    remaining_after_pairing = [t for j, t in enumerate(remaining_teams) 
                                             if j != 0 and j != i]
                    
                    rest_of_matchups = find_matchups(remaining_after_pairing)
                    
                    if rest_of_matchups is not None:
                        # Success! Choose home/away based on balance
                        matchup = choose_home_away(first_team, potential_opponent)
                        return [matchup] + rest_of_matchups
            
            # No valid pairing found
            return None
        
        # Try multiple times with different random orderings
        for attempt in range(100):  # Max attempts to avoid infinite loop
            random.shuffle(team_ids)
            matchups = find_matchups(team_ids)
            if matchups is not None:
                print(f"Found valid matchups after {attempt + 1} attempts")
                return matchups
        
        # If we get here, couldn't find valid matchups
        print(f"Could not find valid matchups after 100 attempts")
        print(f"Teams available: {len(team_ids)}")
        print(f"Already played matchups: {len(played_matchups)}")
        return None
    
    def _validate_home_away_balance(self, weekly_matchups: List[List[Tuple[int, int]]], all_teams: List[Dict]):
        """Validate that every team has at least 1 home and 1 away game"""
        home_counts = {team['team_id']: 0 for team in all_teams}
        away_counts = {team['team_id']: 0 for team in all_teams}
        
        # Count home/away games for each team
        for week_matchups in weekly_matchups:
            for away_id, home_id in week_matchups:
                away_counts[away_id] += 1
                home_counts[home_id] += 1
        
        # Check for teams with no home or away games
        teams_with_no_home = []
        teams_with_no_away = []
        
        for team in all_teams:
            team_id = team['team_id']
            team_name = team['team_name']
            
            home_games = home_counts[team_id]
            away_games = away_counts[team_id]
            
            print(f"[PRESEASON_GEN] {team_name}: {home_games} home, {away_games} away")
            
            if home_games == 0:
                teams_with_no_home.append(team_name)
            if away_games == 0:
                teams_with_no_away.append(team_name)
        
        if teams_with_no_home:
            print(f"[PRESEASON_GEN] ⚠️  Teams with no home games: {teams_with_no_home}")
        if teams_with_no_away:
            print(f"[PRESEASON_GEN] ⚠️  Teams with no away games: {teams_with_no_away}")
        
        if not teams_with_no_home and not teams_with_no_away:
            print(f"[PRESEASON_GEN] ✓ All teams have at least 1 home and 1 away game!")
    
    def _create_scheduled_games(self, weekly_matchups: List[List[Tuple[int, int]]]) -> List[Dict]:
        """Convert weekly matchups to scheduled games with days"""
        
        scheduled_games = []
        
        for week_num, week_matchups in enumerate(weekly_matchups, 1):
            for game_num, (away_team_id, home_team_id) in enumerate(week_matchups):
                
                # Assign different days to spread games across the week
                days = ['Thursday', 'Friday', 'Saturday', 'Sunday']
                day = days[game_num % len(days)]
                
                game = {
                    'week': week_num,
                    'away_team_id': away_team_id,
                    'home_team_id': home_team_id,
                    'day_of_week': day,
                    'game_notes': f'Preseason Week {week_num}'
                }
                
                scheduled_games.append(game)
        
        return scheduled_games
    
    def _insert_preseason_games(self, league_id: int, season: int, games: List[Dict]):
        """Insert preseason games into database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for game in games:
                cursor.execute("""
                    INSERT INTO games (
                        league_id, season, week, game_type,
                        home_team_id, away_team_id, day_of_week, game_notes,
                        game_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, season, game['week'], 'PRESEASON',
                    game['home_team_id'], game['away_team_id'], 
                    game['day_of_week'], game['game_notes'], 'SCHEDULED'
                ))
            
            conn.commit()


def main():
    """Test/example usage"""
    generator = PreseasonGenerator("pynfl.db")
    success = generator.generate_schedule(league_id=1, season=1)
    print(f"Preseason generation successful: {success}")


if __name__ == "__main__":
    main()
