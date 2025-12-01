# ========================================
# tabs/dashboard/games_window.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from common.widgets.data_grid import DataGrid


class GamesWindow(QWidget):
    """Window showing this week's games"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize games window UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("This Week's Games")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Games grid
        self.games_grid = DataGrid()
        layout.addWidget(self.games_grid)
        
        # TODO: Load this week's games
        self.load_games()
        
    def load_games(self):
        """Load and display this week's games"""
        # TODO: Query database for current week's games
        pass

