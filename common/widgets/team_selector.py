# ========================================
# common/widgets/team_selector.py
# ========================================

from PyQt5.QtWidgets import QComboBox
from database.connection import DatabaseManager


class TeamSelector(QComboBox):
    """Reusable team selection dropdown"""
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.load_teams()
        
    def load_teams(self):
        """Load teams from database"""
        # TODO: Populate combo box with teams
        pass
        
    def get_selected_team_id(self) -> int:
        """Get currently selected team ID"""
        # TODO: Return selected team ID
        pass
