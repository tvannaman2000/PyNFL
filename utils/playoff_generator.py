# Version: 4.0
# File: utils/playoff_generator.py
# Playoff schedule generator with locked seeding via playoff_seeds table
# Properly handles 1980s (6-team) and modern (7-team) playoff formats

from typing import List, Dict, Tuple
import sqlite3


class PlayoffGenerator:
    """
    Playoff schedule generator with locked seeding.
    
    Seeds are calculated once from regular season standings and stored in playoff_seeds table.
    Later rounds use the locked seeds instead of recalculating.
    
    Supports both:
    - 1980s format: 6 teams (3 divisions), seeds 1-2 get byes, 3v6 and 4v5 in wildcard
    - Modern format: 7 teams (4 divisions), seed 1 gets bye, 2v7, 3v6, 4v5 in wildcard
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_connection(self):
        """Get database connection"""
        return self.db_manager.get_connection()
    
    def generate_wildcard_round(self, league_id: int, season: int) -> bool:
        """
        Generate Wild Card round games based on standings.
        
        This also creates/recreates the playoff_seeds table for the season.
        Seeds are locked in playoff_seeds and used for all subsequent rounds.
        """
        try:
            print(f"\n[PLAYOFF_GEN] Generating Wild Card round for League {league_id}, Season {season}")
            
            # Check if regular season is complete
            if not self._is_regular_season_complete(league_id, season):
                print("[PLAYOFF_GEN] ❌ Regular season is not complete yet")
                return False
            
            # Get league configuration
            config = self._get_league_config(league_id)
            if not config:
                print("[PLAYOFF_GEN] ❌ Could not load league configuration")
                return False
            
            playoff_teams = config['playoff_teams_per_conf']
            wildcard_week = config['regular_season_games'] + 1
            
            print(f"[PLAYOFF_GEN] Config: {playoff_teams} teams per conf, wildcard starts week {wildcard_week}")
            
            # Clear existing seeds for this season (if regenerating)
            self._clear_playoff_seeds(league_id, season)
            
            # Get conferences
            conferences = self._get_conferences(league_id)
            if not conferences:
                print("[PLAYOFF_GEN] ❌ No conferences found")
                return False
            
            all_games = []
            game_number = 1
            
            for conf in conferences:
                print(f"\n[PLAYOFF_GEN] Processing {conf['conference_name']}")
                
                # Get playoff seeds (this calculates and stores them in playoff_seeds table)
                seeds = self._calculate_and_store_seeds(
                    league_id, season, conf['conference_id'], 
                    conf['abbreviation'], playoff_teams
                )
                
                if not seeds or len(seeds) < playoff_teams:
                    print(f"[PLAYOFF_GEN] ❌ Could not get {playoff_teams} seeds for {conf['conference_name']}")
                    return False
                
                print(f"[PLAYOFF_GEN] Seeds: {[(s['seed_number'], s['abbreviation']) for s in seeds]}")
                
                # Create wild card matchups
                matchups = self._create_wildcard_matchups(seeds, playoff_teams)
                
                print(f"[PLAYOFF_GEN] Creating {len(matchups)} wild card games")
                
                for home_seed, away_seed in matchups:
                    game = {
                        'week': wildcard_week,
                        'game_type': 'WILDCARD',
                        'playoff_round': 1,
                        'playoff_game_number': game_number,
                        'home_team_id': home_seed['team_id'],
                        'away_team_id': away_seed['team_id'],
                        'playoff_bracket_position': f"{conf['abbreviation']}-WC{game_number}",
                        'day_of_week': 'Saturday' if game_number % 2 == 1 else 'Sunday',
                        'game_notes': f"{conf['abbreviation']} Wild Card: #{away_seed['seed_number']} {away_seed['abbreviation']} @ #{home_seed['seed_number']} {home_seed['abbreviation']}"
                    }
                    all_games.append(game)
                    game_number += 1
            
            # Insert games
            self._insert_playoff_games(league_id, season, all_games)
            
            print(f"\n[PLAYOFF_GEN] ✅ Created {len(all_games)} Wild Card games")
            print(f"[PLAYOFF_GEN] ✅ Playoff seeds locked in playoff_seeds table")
            return True
            
        except Exception as e:
            print(f"[PLAYOFF_GEN] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_divisional_round(self, league_id: int, season: int) -> bool:
        """
        Generate Divisional round games based on Wild Card results.
        
        For 6-team format (1980s):
        - Seeds 1 and 2 have byes
        - Winners of 3v6 and 4v5 advance
        - Matchups: lowest remaining seed @ #1, next lowest @ #2
        
        For 7-team format (modern):
        - Seed 1 has bye
        - Winners of 2v7, 3v6, 4v5 advance
        - Matchups: lowest remaining seed @ #1, next two play each other
        """
        try:
            print(f"\n[PLAYOFF_GEN] Generating Divisional round for League {league_id}, Season {season}")
            
            # Check that seeds exist
            if not self._seeds_exist(league_id, season):
                print("[PLAYOFF_GEN] ❌ No playoff seeds found. Generate Wild Card round first.")
                return False
            
            config = self._get_league_config(league_id)
            if not config:
                return False
            
            playoff_teams = config['playoff_teams_per_conf']
            divisional_week = config['regular_season_games'] + 2
            wildcard_week = config['regular_season_games'] + 1
            
            conferences = self._get_conferences(league_id)
            if not conferences:
                return False
            
            all_games = []
            game_number = 1
            
            for conf in conferences:
                print(f"\n[PLAYOFF_GEN] Processing {conf['conference_name']} Divisional Round")
                
                # Get wildcard winners
                wildcard_winners = self._get_wildcard_winners(
                    league_id, season, conf['conference_id'], wildcard_week
                )
                
                # Determine number of byes
                if playoff_teams == 7:
                    num_byes = 1
                elif playoff_teams == 6:
                    num_byes = 2
                elif playoff_teams == 5:
                    num_byes = 1
                elif playoff_teams == 4:
                    num_byes = 0
                else:
                    num_byes = 1 if playoff_teams % 2 == 1 else 0
                
                # Get bye teams from playoff_seeds
                bye_teams = []
                for seed_num in range(1, num_byes + 1):
                    seed_team = self._get_seed_by_number(
                        league_id, season, conf['conference_id'], seed_num
                    )
                    if seed_team:
                        bye_teams.append(seed_team)
                        print(f"[PLAYOFF_GEN] Bye team: #{seed_num} {seed_team['abbreviation']}")
                
                # Combine bye teams and wildcard winners
                all_remaining_teams = bye_teams + wildcard_winners
                
                # Sort by seed number to get proper matchups
                all_remaining_teams.sort(key=lambda t: t['seed_number'])
                
                print(f"[PLAYOFF_GEN] Remaining teams: {[(t['seed_number'], t['abbreviation']) for t in all_remaining_teams]}")
                
                # Create divisional matchups
                matchups = self._create_divisional_matchups(all_remaining_teams)
                
                print(f"[PLAYOFF_GEN] Creating {len(matchups)} divisional games")
                
                for home_seed, away_seed in matchups:
                    game = {
                        'week': divisional_week,
                        'game_type': 'DIVISIONAL',
                        'playoff_round': 2,
                        'playoff_game_number': game_number,
                        'home_team_id': home_seed['team_id'],
                        'away_team_id': away_seed['team_id'],
                        'playoff_bracket_position': f"{conf['abbreviation']}-DIV{game_number}",
                        'day_of_week': 'Saturday' if game_number % 2 == 1 else 'Sunday',
                        'game_notes': f"{conf['abbreviation']} Divisional: #{away_seed['seed_number']} {away_seed['abbreviation']} @ #{home_seed['seed_number']} {home_seed['abbreviation']}"
                    }
                    all_games.append(game)
                    game_number += 1
            
            # Insert games
            self._insert_playoff_games(league_id, season, all_games)
            
            print(f"\n[PLAYOFF_GEN] ✅ Created {len(all_games)} Divisional games")
            return True
            
        except Exception as e:
            print(f"[PLAYOFF_GEN] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_conference_championship(self, league_id: int, season: int) -> bool:
        """
        Generate Conference Championship games.
        
        Matchup is: Lower remaining seed @ Higher remaining seed
        Winners advance to Super Bowl.
        """
        try:
            print(f"\n[PLAYOFF_GEN] Generating Conference Championships for League {league_id}, Season {season}")
            
            # Check that seeds exist
            if not self._seeds_exist(league_id, season):
                print("[PLAYOFF_GEN] ❌ No playoff seeds found. Generate Wild Card round first.")
                return False
            
            config = self._get_league_config(league_id)
            if not config:
                return False
            
            conf_champ_week = config['regular_season_games'] + 3
            divisional_week = config['regular_season_games'] + 2
            
            conferences = self._get_conferences(league_id)
            if not conferences:
                return False
            
            all_games = []
            game_number = 1
            
            for conf in conferences:
                print(f"\n[PLAYOFF_GEN] Processing {conf['conference_name']} Conference Championship")
                
                # Get divisional winners
                divisional_winners = self._get_divisional_winners(
                    league_id, season, conf['conference_id'], divisional_week
                )
                
                if len(divisional_winners) != 2:
                    print(f"[PLAYOFF_GEN] ⚠️ Expected 2 divisional winners, found {len(divisional_winners)}")
                    # Create placeholder game if divisional games not complete
                    placeholder_teams = self._get_playoff_seeds_as_placeholders(
                        league_id, season, conf['conference_id'], 2
                    )
                    if len(placeholder_teams) >= 2:
                        divisional_winners = placeholder_teams[:2]
                    else:
                        print(f"[PLAYOFF_GEN] ❌ Cannot create conference championship for {conf['conference_name']}")
                        continue
                
                # Sort by seed number - lower seed @ higher seed
                divisional_winners.sort(key=lambda t: t['seed_number'])
                home_seed = divisional_winners[0]  # Better seed
                away_seed = divisional_winners[1]  # Worse seed
                
                print(f"[PLAYOFF_GEN] Matchup: #{away_seed['seed_number']} {away_seed['abbreviation']} @ #{home_seed['seed_number']} {home_seed['abbreviation']}")
                
                game = {
                    'week': conf_champ_week,
                    'game_type': 'CONFERENCE',
                    'playoff_round': 3,
                    'playoff_game_number': game_number,
                    'home_team_id': home_seed['team_id'],
                    'away_team_id': away_seed['team_id'],
                    'playoff_bracket_position': f"{conf['abbreviation']}-CONF",
                    'day_of_week': 'Sunday',
                    'game_notes': f"{conf['abbreviation']} Championship: #{away_seed['seed_number']} {away_seed['abbreviation']} @ #{home_seed['seed_number']} {home_seed['abbreviation']}"
                }
                all_games.append(game)
                game_number += 1
            
            # Insert games
            self._insert_playoff_games(league_id, season, all_games)
            
            print(f"\n[PLAYOFF_GEN] ✅ Created {len(all_games)} Conference Championship games")
            return True
            
        except Exception as e:
            print(f"[PLAYOFF_GEN] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_superbowl(self, league_id: int, season: int) -> bool:
        """
        Generate Super Bowl game.
        
        Matchup: Conference champions face off.
        """
        try:
            print(f"\n[PLAYOFF_GEN] Generating Super Bowl for League {league_id}, Season {season}")
            
            config = self._get_league_config(league_id)
            if not config:
                return False
            
            superbowl_week = config['regular_season_games'] + 4
            conf_champ_week = config['regular_season_games'] + 3
            
            conferences = self._get_conferences(league_id)
            if not conferences or len(conferences) != 2:
                print("[PLAYOFF_GEN] ❌ Need exactly 2 conferences for Super Bowl")
                return False
            
            # Get conference champions
            champions = []
            for conf in conferences:
                winners = self._get_conference_champions(
                    league_id, season, conf['conference_id'], conf_champ_week
                )
                if winners:
                    champions.extend(winners)
            
            if len(champions) != 2:
                print(f"[PLAYOFF_GEN] ⚠️ Expected 2 conference champions, found {len(champions)}")
                # Use placeholders if games not complete
                champions = []
                for conf in conferences:
                    placeholder = self._get_playoff_seeds_as_placeholders(
                        league_id, season, conf['conference_id'], 1
                    )
                    if placeholder:
                        champions.extend(placeholder)
            
            if len(champions) != 2:
                print("[PLAYOFF_GEN] ❌ Cannot create Super Bowl without 2 teams")
                return False
            
            # First conference listed is typically home team (alternates yearly in real NFL)
            home_team = champions[0]
            away_team = champions[1]
            
            print(f"[PLAYOFF_GEN] Super Bowl: {away_team['abbreviation']} vs {home_team['abbreviation']}")
            
            game = {
                'week': superbowl_week,
                'game_type': 'SUPERBOWL',
                'playoff_round': 4,
                'playoff_game_number': 1,
                'home_team_id': home_team['team_id'],
                'away_team_id': away_team['team_id'],
                'playoff_bracket_position': 'SB',
                'day_of_week': 'Sunday',
                'game_notes': f"Super Bowl: {away_team['abbreviation']} vs {home_team['abbreviation']}"
            }
            
            self._insert_playoff_games(league_id, season, [game])
            
            print(f"[PLAYOFF_GEN] ✅ Created Super Bowl")
            return True
            
        except Exception as e:
            print(f"[PLAYOFF_GEN] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== Helper Methods ==========
    
    def _is_regular_season_complete(self, league_id: int, season: int) -> bool:
        """Check if all regular season games are complete"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as incomplete_count
                    FROM games
                    WHERE league_id = ? AND season = ? 
                    AND game_type = 'REGULAR'
                    AND game_status != 'COMPLETED'
                """, (league_id, season))
                
                result = cursor.fetchone()
                incomplete = result['incomplete_count'] if result else 0
                
                if incomplete > 0:
                    print(f"[PLAYOFF_GEN] {incomplete} regular season games still incomplete")
                    return False
                return True
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error checking season completion: {e}")
            return False
    
    def _seeds_exist(self, league_id: int, season: int) -> bool:
        """Check if playoff seeds exist for this season"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as seed_count
                    FROM playoff_seeds
                    WHERE league_id = ? AND season = ?
                """, (league_id, season))
                
                result = cursor.fetchone()
                return result['seed_count'] > 0 if result else False
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error checking seeds: {e}")
            return False
    
    def _clear_playoff_seeds(self, league_id: int, season: int):
        """Clear existing playoff seeds for regeneration"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM playoff_seeds
                    WHERE league_id = ? AND season = ?
                """, (league_id, season))
                conn.commit()
                print(f"[PLAYOFF_GEN] Cleared existing seeds for season {season}")
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error clearing seeds: {e}")
    
    def _get_league_config(self, league_id: int) -> Dict:
        """Get league configuration"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT regular_season_games, playoff_teams_per_conf
                    FROM leagues
                    WHERE league_id = ? AND is_active = TRUE
                """, (league_id,))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting league config: {e}")
            return None
    
    def _get_conferences(self, league_id: int) -> List[Dict]:
        """Get all conferences for the league"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conference_id, conference_name, abbreviation
                    FROM conferences
                    WHERE league_id = ? AND is_active = TRUE
                    ORDER BY conference_id
                """, (league_id,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting conferences: {e}")
            return []
    
    def _calculate_and_store_seeds(self, league_id: int, season: int, conference_id: int,
                                   conference_abbr: str, num_playoff_teams: int) -> List[Dict]:
        """Calculate playoff seeds from standings using NFL tie-breaker rules and store in playoff_seeds table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count divisions
                cursor.execute("""
                    SELECT COUNT(*) as div_count
                    FROM divisions
                    WHERE conference_id = ?
                """, (conference_id,))
                
                div_result = cursor.fetchone()
                num_divisions = div_result['div_count'] if div_result else 0
                
                print(f"[PLAYOFF_GEN] Conference has {num_divisions} divisions")
                
                # Get all teams in conference with their records
                cursor.execute("""
                    SELECT 
                        t.team_id,
                        t.full_name as team_name,
                        t.abbreviation,
                        t.division_id,
                        d.division_name,
                        COALESCE(SUM(CASE 
                            WHEN (g.home_team_id = t.team_id AND g.home_score > g.away_score) OR
                                 (g.away_team_id = t.team_id AND g.away_score > g.home_score)
                            THEN 1 ELSE 0 END), 0) as wins,
                        COALESCE(SUM(CASE 
                            WHEN (g.home_team_id = t.team_id AND g.home_score < g.away_score) OR
                                 (g.away_team_id = t.team_id AND g.away_score < g.home_score)
                            THEN 1 ELSE 0 END), 0) as losses,
                        COALESCE(SUM(CASE 
                            WHEN (g.home_team_id = t.team_id OR g.away_team_id = t.team_id) 
                                 AND g.home_score = g.away_score AND g.game_status = 'COMPLETED'
                            THEN 1 ELSE 0 END), 0) as ties
                    FROM teams t
                    JOIN divisions d ON t.division_id = d.division_id
                    LEFT JOIN games g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
                        AND g.league_id = ? AND g.season = ? AND g.game_type = 'REGULAR'
                        AND g.game_status = 'COMPLETED'
                    WHERE t.conference_id = ? AND t.is_active = TRUE
                    GROUP BY t.team_id, t.full_name, t.abbreviation, t.division_id, d.division_name
                """, (league_id, season, conference_id))
                
                teams = cursor.fetchall()
                
                if not teams:
                    print(f"[PLAYOFF_GEN] No teams found in conference")
                    return None
                
                # Calculate win percentage and tie-breaker stats for each team
                teams_with_tiebreakers = []
                for team in teams:
                    team_id = team['team_id']
                    
                    # Get tie-breaker stats
                    h2h_wins, h2h_losses = self._get_head_to_head_record(cursor, team_id, team['division_id'], season, league_id)
                    div_wins, div_losses = self._get_division_record(cursor, team_id, team['division_id'], season, league_id)
                    conf_wins, conf_losses = self._get_conference_record(cursor, team_id, conference_id, season, league_id)
                    points_diff = self._get_points_differential(cursor, team_id, season, league_id)
                    points_for = self._get_points_scored(cursor, team_id, season, league_id)
                    
                    total_games = team['wins'] + team['losses'] + team['ties']
                    win_pct = team['wins'] / total_games if total_games > 0 else 0.0
                    
                    teams_with_tiebreakers.append({
                        'team_id': team_id,
                        'team_name': team['team_name'],
                        'abbreviation': team['abbreviation'],
                        'division_id': team['division_id'],
                        'division_name': team['division_name'],
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
                
                # Find division winners using tie-breakers
                divisions = {}
                for team in teams_with_tiebreakers:
                    div_id = team['division_id']
                    if div_id not in divisions:
                        divisions[div_id] = []
                    divisions[div_id].append(team)
                
                # Get best team from each division using tie-breakers
                division_winners = []
                for div_id, div_teams in divisions.items():
                    sorted_teams = self._sort_teams_with_tiebreakers(div_teams)
                    winner = sorted_teams[0]
                    winner['is_division_winner'] = True
                    division_winners.append(winner)
                
                # Sort division winners by record using tie-breakers
                division_winners = self._sort_teams_with_tiebreakers(division_winners)
                
                # Get wildcards (non-division winners) using tie-breakers
                wildcard_candidates = [t for t in teams_with_tiebreakers 
                                      if not any(t['team_id'] == w['team_id'] 
                                               for w in division_winners)]
                wildcard_candidates = self._sort_teams_with_tiebreakers(wildcard_candidates)
                
                # Combine for final seeds
                seeds = []
                
                # Seeds 1-N: Division winners
                for i, team in enumerate(division_winners, 1):
                    team['seed_number'] = i
                    team['seed_type'] = 'Division Winner'
                    seeds.append(team)
                
                # Remaining seeds: Wildcards
                num_wildcards = num_playoff_teams - len(division_winners)
                for i, team in enumerate(wildcard_candidates[:num_wildcards], len(division_winners) + 1):
                    team['seed_number'] = i
                    team['seed_type'] = 'Wild Card'
                    team['is_division_winner'] = False
                    seeds.append(team)
                
                # Store seeds in database
                for seed in seeds[:num_playoff_teams]:
                    cursor.execute("""
                        INSERT INTO playoff_seeds (
                            league_id, season, conference_id, team_id, seed_number,
                            is_division_winner, division_id, seed_type,
                            wins, losses, ties, win_pct
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        league_id, season, conference_id, seed['team_id'], seed['seed_number'],
                        seed['is_division_winner'], seed['division_id'], seed['seed_type'],
                        seed['wins'], seed['losses'], seed['ties'], seed['win_pct']
                    ))
                
                conn.commit()
                
                return seeds[:num_playoff_teams]
                
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error calculating seeds: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_wildcard_matchups(self, seeds: List[Dict], num_teams: int) -> List[Tuple[Dict, Dict]]:
        """
        Create wild card matchups.
        Top seed(s) get bye(s), remaining teams play.
        
        Logic for common playoff formats:
        - 7 teams: 1 bye (#1), 3 games: #2v7, #3v6, #4v5
        - 6 teams: 2 byes (#1, #2), 2 games: #3v6, #4v5
        - 5 teams: 1 bye (#1), 2 games: #2v5, #3v4
        - 4 teams: 0 byes, 2 games: #1v4, #2v3
        """
        # Determine byes based on playoff structure
        if num_teams == 7:
            num_byes = 1  # #1 seed gets bye (modern NFL)
        elif num_teams == 6:
            num_byes = 2  # #1 and #2 seeds get byes (1980s NFL)
        elif num_teams == 5:
            num_byes = 1  # #1 seed gets bye
        elif num_teams == 4:
            num_byes = 0  # No byes, all play
        else:
            # For other configurations, top seed gets bye if odd number
            num_byes = 1 if num_teams % 2 == 1 else 0
        
        print(f"[PLAYOFF_GEN] {num_teams} teams, {num_byes} bye(s)")
        
        teams_playing = seeds[num_byes:]
        matchups = []
        
        # Pair best vs worst
        num_games = len(teams_playing) // 2
        print(f"[PLAYOFF_GEN] {len(teams_playing)} teams playing, {num_games} games")
        
        for i in range(num_games):
            home_seed = teams_playing[i]
            away_seed = teams_playing[-(i+1)]
            matchups.append((home_seed, away_seed))
            print(f"[PLAYOFF_GEN] Game: #{away_seed['seed_number']} @ #{home_seed['seed_number']}")
        
        return matchups
    
    def _create_divisional_matchups(self, remaining_teams: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        Create divisional round matchups.
        Best remaining seed plays worst remaining seed, etc.
        
        Example for 4 teams (seeds 1,2,3,4): #4@#1, #3@#2
        """
        matchups = []
        num_games = len(remaining_teams) // 2
        
        for i in range(num_games):
            home_seed = remaining_teams[i]
            away_seed = remaining_teams[-(i+1)]
            matchups.append((home_seed, away_seed))
            print(f"[PLAYOFF_GEN] Divisional: #{away_seed['seed_number']} @ #{home_seed['seed_number']}")
        
        return matchups
    
    def _get_wildcard_winners(self, league_id: int, season: int, conference_id: int, wildcard_week: int) -> List[Dict]:
        """Get teams that won their Wild Card games, with their seed info"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get Wild Card games for this conference
                query = """
                    SELECT 
                        g.game_id,
                        g.home_team_id,
                        g.away_team_id,
                        g.home_score,
                        g.away_score,
                        g.game_status,
                        CASE 
                            WHEN g.home_score > g.away_score THEN g.home_team_id
                            WHEN g.away_score > g.home_score THEN g.away_team_id
                            ELSE NULL
                        END as winner_team_id
                    FROM games g
                    JOIN teams home ON g.home_team_id = home.team_id
                    JOIN teams away ON g.away_team_id = away.team_id
                    WHERE g.league_id = ? 
                      AND g.season = ? 
                      AND g.week = ?
                      AND g.game_type = 'WILDCARD'
                      AND home.conference_id = ?
                      AND away.conference_id = ?
                      AND g.game_status = 'COMPLETED'
                """
                
                cursor.execute(query, (league_id, season, wildcard_week, conference_id, conference_id))
                games = cursor.fetchall()
                
                print(f"[PLAYOFF_GEN] Found {len(games)} completed Wild Card games for conference")
                
                # Get winner info with seeds
                winners = []
                for game in games:
                    if game['winner_team_id']:
                        # Get seed info for winner
                        cursor.execute("""
                            SELECT ps.team_id, ps.seed_number, t.full_name as team_name, t.abbreviation
                            FROM playoff_seeds ps
                            JOIN teams t ON ps.team_id = t.team_id
                            WHERE ps.league_id = ? AND ps.season = ? 
                              AND ps.team_id = ? AND ps.conference_id = ?
                        """, (league_id, season, game['winner_team_id'], conference_id))
                        
                        winner_info = cursor.fetchone()
                        if winner_info:
                            winners.append(dict(winner_info))
                            print(f"[PLAYOFF_GEN] Wild Card winner: #{winner_info['seed_number']} {winner_info['abbreviation']}")
                
                return winners
                
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting Wild Card winners: {e}")
            return []
    
    def _get_divisional_winners(self, league_id: int, season: int, conference_id: int, divisional_week: int) -> List[Dict]:
        """Get teams that won their Divisional games, with their seed info"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        g.game_id,
                        CASE 
                            WHEN g.home_score > g.away_score THEN g.home_team_id
                            WHEN g.away_score > g.home_score THEN g.away_team_id
                            ELSE NULL
                        END as winner_team_id
                    FROM games g
                    JOIN teams home ON g.home_team_id = home.team_id
                    JOIN teams away ON g.away_team_id = away.team_id
                    WHERE g.league_id = ? 
                      AND g.season = ? 
                      AND g.week = ?
                      AND g.game_type = 'DIVISIONAL'
                      AND home.conference_id = ?
                      AND away.conference_id = ?
                      AND g.game_status = 'COMPLETED'
                """
                
                cursor.execute(query, (league_id, season, divisional_week, conference_id, conference_id))
                games = cursor.fetchall()
                
                print(f"[PLAYOFF_GEN] Found {len(games)} completed Divisional games for conference")
                
                winners = []
                for game in games:
                    if game['winner_team_id']:
                        cursor.execute("""
                            SELECT ps.team_id, ps.seed_number, t.full_name as team_name, t.abbreviation
                            FROM playoff_seeds ps
                            JOIN teams t ON ps.team_id = t.team_id
                            WHERE ps.league_id = ? AND ps.season = ? 
                              AND ps.team_id = ? AND ps.conference_id = ?
                        """, (league_id, season, game['winner_team_id'], conference_id))
                        
                        winner_info = cursor.fetchone()
                        if winner_info:
                            winners.append(dict(winner_info))
                            print(f"[PLAYOFF_GEN] Divisional winner: #{winner_info['seed_number']} {winner_info['abbreviation']}")
                
                return winners
                
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting Divisional winners: {e}")
            return []
    
    def _get_conference_champions(self, league_id: int, season: int, conference_id: int, conf_champ_week: int) -> List[Dict]:
        """Get conference champion with seed info"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        CASE 
                            WHEN g.home_score > g.away_score THEN g.home_team_id
                            WHEN g.away_score > g.home_score THEN g.away_team_id
                            ELSE NULL
                        END as winner_team_id
                    FROM games g
                    JOIN teams home ON g.home_team_id = home.team_id
                    JOIN teams away ON g.away_team_id = away.team_id
                    WHERE g.league_id = ? 
                      AND g.season = ? 
                      AND g.week = ?
                      AND g.game_type = 'CONFERENCE'
                      AND home.conference_id = ?
                      AND away.conference_id = ?
                      AND g.game_status = 'COMPLETED'
                """
                
                cursor.execute(query, (league_id, season, conf_champ_week, conference_id, conference_id))
                game = cursor.fetchone()
                
                if game and game['winner_team_id']:
                    cursor.execute("""
                        SELECT ps.team_id, ps.seed_number, t.full_name as team_name, t.abbreviation
                        FROM playoff_seeds ps
                        JOIN teams t ON ps.team_id = t.team_id
                        WHERE ps.league_id = ? AND ps.season = ? 
                          AND ps.team_id = ? AND ps.conference_id = ?
                    """, (league_id, season, game['winner_team_id'], conference_id))
                    
                    winner_info = cursor.fetchone()
                    if winner_info:
                        print(f"[PLAYOFF_GEN] Conference champion: #{winner_info['seed_number']} {winner_info['abbreviation']}")
                        return [dict(winner_info)]
                
                return []
                
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting conference champion: {e}")
            return []
    
    def _get_seed_by_number(self, league_id: int, season: int, conference_id: int, seed_number: int) -> Dict:
        """Get a specific seed from playoff_seeds table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ps.team_id, ps.seed_number, t.full_name as team_name, t.abbreviation
                    FROM playoff_seeds ps
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? 
                      AND ps.conference_id = ? AND ps.seed_number = ?
                """, (league_id, season, conference_id, seed_number))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting seed: {e}")
            return None
    
    def _get_playoff_seeds_as_placeholders(self, league_id: int, season: int, conference_id: int, limit: int) -> List[Dict]:
        """Get playoff seeds to use as placeholders when games aren't complete yet"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ps.team_id, ps.seed_number, t.full_name as team_name, t.abbreviation
                    FROM playoff_seeds ps
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.conference_id = ?
                    ORDER BY ps.seed_number
                    LIMIT ?
                """, (league_id, season, conference_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error getting placeholder seeds: {e}")
            return []
    
    def _insert_playoff_games(self, league_id: int, season: int, games: List[Dict]):
        """Insert playoff games into database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for game in games:
                    cursor.execute("""
                        INSERT INTO games (
                            league_id, season, week, game_type,
                            home_team_id, away_team_id,
                            playoff_round, playoff_game_number, playoff_bracket_position,
                            day_of_week, game_notes, game_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        league_id, season, game['week'], game['game_type'],
                        game['home_team_id'], game['away_team_id'],
                        game['playoff_round'], game['playoff_game_number'], 
                        game['playoff_bracket_position'],
                        game['day_of_week'], game['game_notes'], 'SCHEDULED'
                    ))
                
                conn.commit()
                print(f"[PLAYOFF_GEN] Inserted {len(games)} games into database")
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error inserting games: {e}")
            raise
    
    def clear_playoff_games(self, league_id: int, season: int) -> bool:
        """Clear all playoff games AND seeds for a season"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clear games
                cursor.execute("""
                    DELETE FROM games
                    WHERE league_id = ? AND season = ?
                    AND game_type IN ('WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL')
                """, (league_id, season))
                
                # Clear seeds
                cursor.execute("""
                    DELETE FROM playoff_seeds
                    WHERE league_id = ? AND season = ?
                """, (league_id, season))
                
                conn.commit()
                print(f"[PLAYOFF_GEN] Cleared playoff games and seeds for season {season}")
                return True
        except Exception as e:
            print(f"[PLAYOFF_GEN] Error clearing playoff games: {e}")
            return False
    
    # ========== NFL Tie-Breaker Helper Methods ==========
    
    def _sort_teams_with_tiebreakers(self, teams: List[Dict]) -> List[Dict]:
        """
        Sort teams using NFL tie-breaker rules.
        
        Tie-breaker order:
        1. Win percentage (primary)
        2. Head-to-head win percentage
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
    
    def _get_head_to_head_record(self, cursor, team_id: int, division_id: int, season: int, league_id: int) -> Tuple[int, int]:
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
    
    def _get_division_record(self, cursor, team_id: int, division_id: int, season: int, league_id: int) -> Tuple[int, int]:
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
    
    def _get_conference_record(self, cursor, team_id: int, conference_id: int, season: int, league_id: int) -> Tuple[int, int]:
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
    
    def _get_points_differential(self, cursor, team_id: int, season: int, league_id: int) -> int:
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
    
    def _get_points_scored(self, cursor, team_id: int, season: int, league_id: int) -> int:
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
