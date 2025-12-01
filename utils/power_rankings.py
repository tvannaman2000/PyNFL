# ========================================
# utils/power_rankings.py
# Version: 2.0
# Path: utils/power_rankings.py
# ========================================

"""
Power Rankings Calculator

ELO-style rating system with recency weighting and asymmetric loss penalty.
Recent games matter more, and losses hurt more than wins help.
"""

import sqlite3
from datetime import datetime

class PowerRankingsCalculator:
    """Calculate and update team power rankings using weighted ELO system"""
    
    def __init__(self, db_path, k_factor_win=32, k_factor_loss=48, initial_rating=1500):
        self.db_path = db_path
        self.k_factor_win = k_factor_win  # Points gained for winning
        self.k_factor_loss = k_factor_loss  # Points lost for losing (higher = more penalty)
        self.initial_rating = initial_rating
        
        # Recency decay settings
        self.recent_games_full_weight = 5  # Last 5 games at 100%
        self.medium_games_half_weight = 5  # Games 6-10 at 50%
        # Games 11+ at 25%
    
    def calculate_game_weight(self, games_ago):
        """
        Calculate weight for a game based on how many games ago it was.
        
        Args:
            games_ago: How many games in the past (0 = most recent)
        
        Returns:
            Weight multiplier (0.25 to 1.0)
        """
        if games_ago < self.recent_games_full_weight:
            return 1.0  # Full weight for last 5 games
        elif games_ago < self.recent_games_full_weight + self.medium_games_half_weight:
            return 0.5  # Half weight for games 6-10
        else:
            return 0.25  # Quarter weight for older games
    
    def calculate_expected_score(self, rating_a, rating_b):
        """Calculate expected win probability for team A"""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, winner_rating, loser_rating, game_weight=1.0):
        """
        Calculate new ratings after a game with asymmetric K-factors.
        
        Args:
            winner_rating: Current rating of winning team
            loser_rating: Current rating of losing team
            game_weight: Recency weight (0.25 to 1.0)
        
        Returns:
            Tuple of (new_winner_rating, new_loser_rating)
        """
        expected_winner = self.calculate_expected_score(winner_rating, loser_rating)
        expected_loser = self.calculate_expected_score(loser_rating, winner_rating)
        
        # Winners gain points based on k_factor_win
        # Losers lose points based on k_factor_loss (which is higher)
        winner_change = self.k_factor_win * (1 - expected_winner) * game_weight
        loser_change = self.k_factor_loss * (0 - expected_loser) * game_weight
        
        new_winner_rating = winner_rating + winner_change
        new_loser_rating = loser_rating + loser_change
        
        return new_winner_rating, new_loser_rating
    
    def initialize_team_ratings(self):
        """Initialize all teams with base rating"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Create power_rankings table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS power_rankings (
                    team_id INTEGER PRIMARY KEY,
                    current_rating REAL NOT NULL,
                    games_counted INTEGER DEFAULT 0,
                    last_updated TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams(team_id)
                )
            """)
            
            # Get all active teams
            cursor.execute("SELECT team_id FROM teams WHERE is_active = 1")
            teams = cursor.fetchall()
            
            # Initialize ratings for teams that don't have them
            for team in teams:
                cursor.execute("""
                    INSERT OR IGNORE INTO power_rankings (team_id, current_rating, games_counted, last_updated)
                    VALUES (?, ?, 0, ?)
                """, (team['team_id'], self.initial_rating, datetime.now()))
            
            conn.commit()
            print(f"Initialized {len(teams)} teams with rating {self.initial_rating}")
            
        finally:
            conn.close()
    
    def update_all_rankings(self, season=None):
        """
        Process all completed games and update rankings with recency weighting.
        Each game is processed once with appropriate weights for both teams.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Initialize ratings first
            self.initialize_team_ratings()
            
            # Reset all ratings to initial value
            cursor.execute("""
                UPDATE power_rankings 
                SET current_rating = ?, games_counted = 0
            """, (self.initial_rating,))
            
            # Get all completed games, ordered by season and week
            query = """
                SELECT game_id, home_team_id, away_team_id, home_score, away_score, season, week
                FROM games
                WHERE game_status = 'COMPLETED'
            """
            
            if season is not None:
                query += f" AND season = {season}"
            
            query += " ORDER BY season, week, game_id"
            
            cursor.execute(query)
            all_games = cursor.fetchall()
            
            if not all_games:
                print("No completed games found")
                return False
            
            print(f"Processing {len(all_games)} completed games...")
            
            # Build team game history to calculate recency weights
            team_game_history = {}  # team_id -> list of game_ids in chronological order
            
            for game in all_games:
                home_id = game['home_team_id']
                away_id = game['away_team_id']
                game_id = game['game_id']
                
                if home_id not in team_game_history:
                    team_game_history[home_id] = []
                if away_id not in team_game_history:
                    team_game_history[away_id] = []
                
                team_game_history[home_id].append(game_id)
                team_game_history[away_id].append(game_id)
            
            # Process each game once, applying appropriate weights for each team
            for game in all_games:
                home_id = game['home_team_id']
                away_id = game['away_team_id']
                game_id = game['game_id']
                
                # Get current ratings
                cursor.execute("SELECT current_rating FROM power_rankings WHERE team_id = ?", (home_id,))
                home_rating = cursor.fetchone()['current_rating']
                
                cursor.execute("SELECT current_rating FROM power_rankings WHERE team_id = ?", (away_id,))
                away_rating = cursor.fetchone()['current_rating']
                
                # Calculate recency weight for each team based on their game history
                home_games = team_game_history[home_id]
                away_games = team_game_history[away_id]
                
                home_game_idx = home_games.index(game_id)
                away_game_idx = away_games.index(game_id)
                
                home_games_ago = len(home_games) - home_game_idx - 1
                away_games_ago = len(away_games) - away_game_idx - 1
                
                home_weight = self.calculate_game_weight(home_games_ago)
                away_weight = self.calculate_game_weight(away_games_ago)
                
                # Use average weight for the game (both teams affected equally)
                avg_weight = (home_weight + away_weight) / 2.0
                
                # Determine winner and calculate new ratings
                if game['home_score'] > game['away_score']:
                    winner_id = home_id
                    loser_id = away_id
                    new_winner_rating, new_loser_rating = self.update_ratings(
                        home_rating, away_rating, avg_weight)
                else:
                    winner_id = away_id
                    loser_id = home_id
                    new_winner_rating, new_loser_rating = self.update_ratings(
                        away_rating, home_rating, avg_weight)
                
                # Update ratings in database
                cursor.execute("""
                    UPDATE power_rankings 
                    SET current_rating = ?, games_counted = games_counted + 1, last_updated = ?
                    WHERE team_id = ?
                """, (new_winner_rating, datetime.now(), winner_id))
                
                cursor.execute("""
                    UPDATE power_rankings 
                    SET current_rating = ?, games_counted = games_counted + 1, last_updated = ?
                    WHERE team_id = ?
                """, (new_loser_rating, datetime.now(), loser_id))
            
            conn.commit()
            
            print(f"Successfully updated power rankings using {len(all_games)} games")
            print(f"Recency settings: Last {self.recent_games_full_weight} games = 100% weight")
            print(f"Loss penalty K-factor: {self.k_factor_loss} (vs win K-factor: {self.k_factor_win})")
            
            return True
            
        except Exception as e:
            print(f"Error updating rankings: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def calculate_win_percentage_adjustment(self, cursor, team_id, season):
        """
        Calculate adjustment to rating based on overall win percentage.
        Teams with better records get a bonus, worse records get a penalty.
        
        Returns:
            Rating adjustment value
        """
        # Get team's record for the season
        query = """
            SELECT 
                SUM(CASE 
                    WHEN (home_team_id = ? AND home_score > away_score) THEN 1
                    WHEN (away_team_id = ? AND away_score > home_score) THEN 1
                    ELSE 0
                END) as wins,
                SUM(CASE 
                    WHEN (home_team_id = ? AND home_score < away_score) THEN 1
                    WHEN (away_team_id = ? AND away_score < home_score) THEN 1
                    ELSE 0
                END) as losses,
                COUNT(*) as total_games
            FROM games
            WHERE game_status = 'COMPLETED'
            AND season = ?
            AND (home_team_id = ? OR away_team_id = ?)
        """
        
        cursor.execute(query, (team_id, team_id, team_id, team_id, season, team_id, team_id))
        result = cursor.fetchone()
        
        wins = result['wins'] or 0
        losses = result['losses'] or 0
        total_games = result['total_games'] or 0
        
        if total_games == 0:
            return 0
        
        win_pct = wins / total_games
        
        # Calculate adjustment based on win percentage
        # .500 = no adjustment
        # .600 = +60 points
        # .700 = +120 points
        # .400 = -60 points
        # .300 = -120 points
        adjustment = (win_pct - 0.5) * 600
        
        return adjustment
    
    def get_rankings(self, limit=None, season=None):
        """
        Get current power rankings sorted by adjusted rating.
        Adjusted rating = ELO rating + win percentage bonus/penalty
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # If no season specified, get current season
            if season is None:
                cursor.execute("SELECT current_season FROM leagues WHERE is_active = 1 LIMIT 1")
                season_result = cursor.fetchone()
                if season_result:
                    season = season_result['current_season']
                else:
                    season = 1
            
            # Get base ratings
            cursor.execute("""
                SELECT 
                    pr.team_id,
                    t.full_name,
                    t.abbreviation,
                    pr.current_rating,
                    pr.games_counted,
                    pr.last_updated
                FROM power_rankings pr
                JOIN teams t ON pr.team_id = t.team_id
            """)
            
            teams = cursor.fetchall()
            
            # Calculate adjusted ratings with win percentage bonus
            rankings = []
            for team in teams:
                win_pct_adj = self.calculate_win_percentage_adjustment(
                    cursor, team['team_id'], season)
                
                adjusted_rating = team['current_rating'] + win_pct_adj
                
                rankings.append({
                    'team_id': team['team_id'],
                    'full_name': team['full_name'],
                    'abbreviation': team['abbreviation'],
                    'current_rating': adjusted_rating,
                    'base_rating': team['current_rating'],
                    'win_pct_adjustment': win_pct_adj,
                    'games_counted': team['games_counted'],
                    'last_updated': team['last_updated']
                })
            
            # Sort by adjusted rating
            rankings.sort(key=lambda x: x['current_rating'], reverse=True)
            
            # Apply limit if specified
            if limit:
                rankings = rankings[:limit]
            
            return rankings
            
        finally:
            conn.close()
