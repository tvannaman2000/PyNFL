# ========================================
# utils/age_players.py
# Version: 1.0
# Path: utils/age_players.py
# ========================================

"""
Age Players Utility

Handles the offseason task of aging all players by one year.
This is a simple but important offseason maintenance task.
"""

from datetime import datetime


class AgePlayersProcessor:
    """Processor for aging all players in the league"""
    
    def __init__(self, db_path):
        """
        Initialize the age players processor
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
    
    def age_all_players(self, league_id, season):
        """
        Age all players in the league by one year
        
        Args:
            league_id: ID of the league
            season: Season number (for tracking/metadata)
            
        Returns:
            dict: Results containing:
                - success: bool
                - players_aged: int (number of players aged)
                - error: str (if failed)
                - details: dict (breakdown by position, age ranges, etc.)
        """
        import sqlite3
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            print(f"[AGE_PLAYERS] Starting age players process for league {league_id}, season {season}")
            
            # Get count before aging
            cursor.execute("""
                SELECT COUNT(*) as total_players
                FROM players
                WHERE league_id = ?
            """, (league_id,))
            
            result = cursor.fetchone()
            total_players = result['total_players'] if result else 0
            
            if total_players == 0:
                return {
                    'success': False,
                    'players_aged': 0,
                    'error': 'No players found in league',
                    'details': {}
                }
            
            print(f"[AGE_PLAYERS] Found {total_players} players to age")
            
            # Get age distribution before aging (for reporting)
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN age < 25 THEN 1 END) as under_25,
                    COUNT(CASE WHEN age BETWEEN 25 AND 29 THEN 1 END) as age_25_29,
                    COUNT(CASE WHEN age BETWEEN 30 AND 34 THEN 1 END) as age_30_34,
                    COUNT(CASE WHEN age >= 35 THEN 1 END) as age_35_plus,
                    MIN(age) as youngest,
                    MAX(age) as oldest,
                    AVG(age) as avg_age
                FROM players
                WHERE league_id = ?
            """, (league_id,))
            
            before_stats = cursor.fetchone()
            
            # Age all players by 1 year
            cursor.execute("""
                UPDATE players
                SET age = age + 1
                WHERE league_id = ?
            """, (league_id,))
            
            rows_updated = cursor.rowcount
            
            print(f"[AGE_PLAYERS] Aged {rows_updated} players")
            
            # Get age distribution after aging
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN age < 25 THEN 1 END) as under_25,
                    COUNT(CASE WHEN age BETWEEN 25 AND 29 THEN 1 END) as age_25_29,
                    COUNT(CASE WHEN age BETWEEN 30 AND 34 THEN 1 END) as age_30_34,
                    COUNT(CASE WHEN age >= 35 THEN 1 END) as age_35_plus,
                    MIN(age) as youngest,
                    MAX(age) as oldest,
                    AVG(age) as avg_age
                FROM players
                WHERE league_id = ?
            """, (league_id,))
            
            after_stats = cursor.fetchone()
            
            # Get breakdown by position
            cursor.execute("""
                SELECT 
                    position,
                    COUNT(*) as player_count,
                    AVG(age) as avg_age
                FROM players
                WHERE league_id = ?
                GROUP BY position
                ORDER BY position
            """, (league_id,))
            
            position_breakdown = []
            for row in cursor.fetchall():
                position_breakdown.append({
                    'position': row['position'],
                    'count': row['player_count'],
                    'avg_age': round(row['avg_age'], 1)
                })
            
            # Commit the changes
            conn.commit()
            
            # Build results
            details = {
                'before': {
                    'under_25': before_stats['under_25'],
                    'age_25_29': before_stats['age_25_29'],
                    'age_30_34': before_stats['age_30_34'],
                    'age_35_plus': before_stats['age_35_plus'],
                    'youngest': before_stats['youngest'],
                    'oldest': before_stats['oldest'],
                    'avg_age': round(before_stats['avg_age'], 1)
                },
                'after': {
                    'under_25': after_stats['under_25'],
                    'age_25_29': after_stats['age_25_29'],
                    'age_30_34': after_stats['age_30_34'],
                    'age_35_plus': after_stats['age_35_plus'],
                    'youngest': after_stats['youngest'],
                    'oldest': after_stats['oldest'],
                    'avg_age': round(after_stats['avg_age'], 1)
                },
                'position_breakdown': position_breakdown,
                'season': season,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"[AGE_PLAYERS] ✅ Successfully aged {rows_updated} players")
            print(f"[AGE_PLAYERS]   Average age: {details['before']['avg_age']} -> {details['after']['avg_age']}")
            print(f"[AGE_PLAYERS]   Players 35+: {details['before']['age_35_plus']} -> {details['after']['age_35_plus']}")
            
            return {
                'success': True,
                'players_aged': rows_updated,
                'error': None,
                'details': details
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            print(f"[AGE_PLAYERS] ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'players_aged': 0,
                'error': str(e),
                'details': {}
            }
            
        finally:
            if conn:
                conn.close()


def age_players(db_path, league_id, season):
    """
    Convenience function to age all players
    
    Args:
        db_path: Path to database
        league_id: League ID
        season: Season number
        
    Returns:
        dict: Results from AgePlayersProcessor
    """
    processor = AgePlayersProcessor(db_path)
    return processor.age_all_players(league_id, season)
