# ========================================
# common/widgets/player_selector.py
# ========================================

from PyQt5.QtWidgets import QComboBox
from database.connection import DatabaseManager


class PlayerSelector(QComboBox):
    """Reusable player selection dropdown"""
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
    def load_players(self, team_id: int = None, position: str = None):
        """Load players with optional filters"""
        # TODO: Populate combo box with filtered players
        pass
