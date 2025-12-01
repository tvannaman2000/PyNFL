# ========================================
# tabs/dashboard/divisional_leaders.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from common.widgets.data_grid import DataGrid


class DivisionalLeadersWindow(QWidget):
    """Window showing divisional standings"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize divisional leaders UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Divisional Leaders")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Standings grid
        self.standings_grid = DataGrid()
        layout.addWidget(self.standings_grid)
        
        self.load_standings()
        
    def load_standings(self):
        """Load divisional standings"""
        # TODO: Query database for divisional standings
        pass
