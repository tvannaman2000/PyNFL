# ========================================
# utils/update_skills.py
# Version: 1.0
# Path: utils/update_skills.py
# ========================================

"""
Update Player Skills Utility

Applies skill progression/regression based on player age and position.
- Young players (under 27): potential for improvement
- Prime players (27-30): maintain or slight improvement  
- Aging players (31+): gradual decline
"""

from datetime import datetime
import random


class PlayerSkillsUpdater:
    """Updates player skills based on age and position"""
    
    # Age thresholds
    YOUNG_MAX = 26
    PRIME_START = 27
    PRIME_END = 30
    DECLINE_START = 31
    RAPID_DECLINE = 35
    
    # Skill names
    SKILLS = ['skill_run', 'skill_pass', 'skill_receive', 'skill_block', 'skill_kick']
    
    # Position decline rates (slower = declines less quickly)
    POSITION_DECLINE_RATES = {
        'QB': 'slow',     # Experience helps
        'K': 'slow',      # Kicking is mental
        'P': 'slow',      # Punting is mental
        'RB': 'fast',     # Speed-dependent
        'WR': 'fast',     # Speed-dependent
        'TE': 'medium',   # Mix of speed and strength
        'OL': 'medium',   # Strength-based
        'DL': 'medium',   # Strength-based
        'LB': 'medium',   # Mix
        'CB': 'fast',     # Speed-dependent
        'S': 'medium'     # Mix
    }
    
    # Position primary skills (decline these first/fastest)
    POSITION_PRIMARY_SKILLS = {
        'QB': ['skill_pass'],
        'RB': ['skill_run', 'skill_receive'],
        'WR': ['skill_receive'],
        'TE': ['skill_receive', 'skill_block'],
        'K': ['skill_kick'],
        'P': ['skill_kick'],
        'OL': ['skill_block'],
        'DL': ['skill_block'],
        'LB': ['skill_block'],
        'CB': ['skill_receive'],  # Coverage
        'S': ['skill_receive']    # Coverage
    }
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_decline_rate(self, position):
        """Get decline rate for position"""
        return self.POSITION_DECLINE_RATES.get(position, 'medium')
    
    def calculate_skill_change(self, age, current_skill, position, skill_name):
        """
        Calculate skill change based on age and position
        
        Args:
            age: Player's age
            current_skill: Current skill rating
            position: Player's position
            skill_name: Name of the skill being updated
            
        Returns:
            int: New skill value
        """
        if current_skill <= 50:
            return current_skill  # Don't change if at minimum
        
        decline_rate = self.get_decline_rate(position)
        is_primary_skill = skill_name in self.POSITION_PRIMARY_SKILLS.get(position, [])
        
        # Young players - potential improvement
        if age <= self.YOUNG_MAX:
            chance = random.random()
            if chance < 0.40:  # 40% chance to improve
                change = random.randint(1, 3)
                return min(99, current_skill + change)
            return current_skill
        
        # Prime players - maintain or slight improvement
        elif age <= self.PRIME_END:
            chance = random.random()
            if chance < 0.20:  # 20% chance to improve
                change = random.randint(1, 2)
                return min(99, current_skill + change)
            return current_skill
        
        # Aging players - decline begins
        elif age <= 32:
            chance = random.random()
            base_chance = 0.30 if decline_rate == 'fast' else 0.20 if decline_rate == 'medium' else 0.15
            
            if is_primary_skill:
                base_chance += 0.10  # Primary skills decline more
            
            if chance < base_chance:
                return max(50, current_skill - 1)
            return current_skill
        
        # 33-34 - noticeable decline
        elif age <= 34:
            chance = random.random()
            
            if decline_rate == 'fast':
                if chance < 0.50:
                    change = -2 if is_primary_skill else -1
                    return max(50, current_skill + change)
            elif decline_rate == 'medium':
                if chance < 0.40:
                    return max(50, current_skill - 1)
            else:  # slow
                if chance < 0.30:
                    return max(50, current_skill - 1)
            
            return current_skill
        
        # 35-36 - significant decline
        elif age <= 36:
            chance = random.random()
            
            if decline_rate == 'fast':
                if chance < 0.70:
                    change = random.choice([-1, -2, -2, -3])  # Weighted toward -2
                    return max(50, current_skill + change)
            elif decline_rate == 'medium':
                if chance < 0.60:
                    change = random.choice([-1, -1, -2])  # Weighted toward -1
                    return max(50, current_skill + change)
            else:  # slow
                if chance < 0.40:
                    return max(50, current_skill - 1)
            
            return current_skill
        
        # 37+ - rapid decline
        else:
            chance = random.random()
            
            if decline_rate == 'fast':
                if chance < 0.90:
                    change = random.choice([-2, -2, -3, -3])
                    return max(50, current_skill + change)
            elif decline_rate == 'medium':
                if chance < 0.80:
                    change = random.choice([-1, -2, -2])
                    return max(50, current_skill + change)
            else:  # slow
                if chance < 0.60:
                    change = random.choice([-1, -1, -2])
                    return max(50, current_skill + change)
            
            return current_skill
    
    def update_all_player_skills(self, league_id, season):
        """
        Update skills for all players in the league
        
        Args:
            league_id: ID of the league
            season: Season number
            
        Returns:
            dict: Results with success, players_updated, and details
        """
        import sqlite3
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            print(f"[UPDATE_SKILLS] Starting skill update for league {league_id}, season {season}")
            
            # Get all players
            cursor.execute("""
                SELECT player_id, age, position, 
                       skill_run, skill_pass, skill_receive, skill_block, skill_kick
                FROM players
                WHERE league_id = ?
            """, (league_id,))
            
            players = cursor.fetchall()
            
            if not players:
                return {
                    'success': False,
                    'players_updated': 0,
                    'error': 'No players found',
                    'details': {}
                }
            
            print(f"[UPDATE_SKILLS] Processing {len(players)} players...")
            
            # Track changes
            players_updated = 0
            total_improvements = 0
            total_declines = 0
            skill_changes = {skill: 0 for skill in self.SKILLS}
            
            # Process each player
            for player in players:
                player_changed = False
                
                for skill_name in self.SKILLS:
                    old_value = player[skill_name]
                    new_value = self.calculate_skill_change(
                        player['age'],
                        old_value,
                        player['position'],
                        skill_name
                    )
                    
                    if new_value != old_value:
                        cursor.execute(f"""
                            UPDATE players
                            SET {skill_name} = ?
                            WHERE player_id = ?
                        """, (new_value, player['player_id']))
                        
                        player_changed = True
                        skill_changes[skill_name] += 1
                        
                        if new_value > old_value:
                            total_improvements += 1
                        else:
                            total_declines += 1
                
                if player_changed:
                    players_updated += 1
            
            conn.commit()
            
            # Calculate statistics
            cursor.execute("""
                SELECT 
                    AVG(skill_run) as avg_run,
                    AVG(skill_pass) as avg_pass,
                    AVG(skill_receive) as avg_receive,
                    AVG(skill_block) as avg_block,
                    AVG(skill_kick) as avg_kick
                FROM players
                WHERE league_id = ?
            """, (league_id,))
            
            avg_skills = cursor.fetchone()
            
            details = {
                'players_updated': players_updated,
                'total_improvements': total_improvements,
                'total_declines': total_declines,
                'skill_changes': skill_changes,
                'avg_skills': {
                    'run': round(avg_skills['avg_run'], 1),
                    'pass': round(avg_skills['avg_pass'], 1),
                    'receive': round(avg_skills['avg_receive'], 1),
                    'block': round(avg_skills['avg_block'], 1),
                    'kick': round(avg_skills['avg_kick'], 1)
                },
                'season': season,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"[UPDATE_SKILLS] ✅ Updated {players_updated} players")
            print(f"[UPDATE_SKILLS]   Improvements: {total_improvements}")
            print(f"[UPDATE_SKILLS]   Declines: {total_declines}")
            
            return {
                'success': True,
                'players_updated': players_updated,
                'error': None,
                'details': details
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            print(f"[UPDATE_SKILLS] ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'players_updated': 0,
                'error': str(e),
                'details': {}
            }
            
        finally:
            if conn:
                conn.close()


def update_player_skills(db_path, league_id, season):
    """
    Convenience function to update all player skills
    
    Args:
        db_path: Path to database
        league_id: League ID
        season: Season number
        
    Returns:
        dict: Results from PlayerSkillsUpdater
    """
    updater = PlayerSkillsUpdater(db_path)
    return updater.update_all_player_skills(league_id, season)
