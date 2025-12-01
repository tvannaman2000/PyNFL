# database/service.py
"""
Database service layer - provides a simple interface for GUI components
to interact with the database models.
"""

from typing import List, Dict, Optional, Tuple
from .connection import DatabaseManager
from .models import LeagueModel, TeamModel, PlayerModel, PositionModel


class DatabaseService:
    """
    Main database service that provides easy access to all database operations.
    Use this class from your GUI components instead of calling models directly.
    """
    
    def __init__(self, db_path: str = "pynfl.db"):
        """Initialize database service"""
        self.db_manager = DatabaseManager(db_path)
        
        # Initialize models
        self.leagues = LeagueModel(self.db_manager)
        self.teams = TeamModel(self.db_manager)
        self.players = PlayerModel(self.db_manager)
        self.positions = PositionModel(self.db_manager)
    
    # ========================================
    # Quick access methods for common operations
    # ========================================
    
    def get_current_season_week(self) -> Tuple[int, int]:
        """Get current season and week"""
        return self.db_manager.get_current_season_week()
    
    def advance_week(self) -> bool:
        """Advance to next week"""
        season, week = self.get_current_season_week()
        
        # Simple logic - you can make this more sophisticated
        if week >= 17:  # End of regular season
            return self.db_manager.update_season_week(season + 1, 1)
        else:
            return self.db_manager.update_season_week(season, week + 1)
    
    def previous_week(self) -> bool:
        """Go back to previous week"""
        season, week = self.get_current_season_week()
        
        if week <= 1:
            if season <= 1:
                return False  # Can't go before season 1, week 1
            return self.db_manager.update_season_week(season - 1, 17)
        else:
            return self.db_manager.update_season_week(season, week - 1)
    
    def get_active_league(self) -> Optional[Dict]:
        """Get the currently active league"""
        return self.db_manager.get_current_league()
    
    def get_all_teams(self) -> List[Dict]:
        """Get all teams in active league"""
        return self.teams.get_all_teams()
    
    def get_team_roster(self, team_id: int) -> List[Dict]:
        """Get team roster"""
        return self.teams.get_team_roster(team_id)
    
    def search_players(self, **criteria) -> List[Dict]:
        """Search players with criteria"""
        return self.players.search_players(criteria)
    
    def get_free_agents(self) -> List[Dict]:
        """Get all free agents"""
        return self.players.get_free_agents()
    
    def get_position_groups(self) -> Dict[str, List[Dict]]:
        """Get positions organized by group"""
        all_positions = self.positions.get_all_positions()
        groups = {}
        
        for pos in all_positions:
            group = pos['position_group']
            if group not in groups:
                groups[group] = []
            groups[group].append(pos)
        
        return groups
    
    # ========================================
    # Settings operations
    # ========================================
    
    def get_league_settings(self) -> Optional[Dict]:
        """Get league settings"""
        return self.db_manager.get_league_settings()
    
    def update_league_settings(self, settings: Dict) -> bool:
        """Update league settings"""
        return self.db_manager.update_league_settings(settings)
    
    # ========================================
    # Statistics and analysis
    # ========================================
    
    def get_top_players_by_position(self, position: str, limit: int = 10) -> List[Dict]:
        """Get top players at a position"""
        return self.players.get_players_by_position(position)[:limit]
    
    def get_team_depth_chart(self, team_id: int) -> Dict[str, List[Dict]]:
        """Get team depth chart organized by position"""
        roster = self.get_team_roster(team_id)
        depth_chart = {}
        
        for player in roster:
            position = player['position_on_team']
            if position not in depth_chart:
                depth_chart[position] = []
            depth_chart[position].append(player)
        
        # Sort each position by depth chart order
        for position in depth_chart:
            depth_chart[position].sort(key=lambda p: p['depth_chart_order'] or 999)
        
        return depth_chart
    
    # ========================================
    # Utility methods
    # ========================================
    
    def test_connection(self) -> bool:
        """Test database connection"""
        return self.db_manager.test_connection()
    
    def close(self):
        """Close database connection"""
        self.db_manager.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
