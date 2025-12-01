# ========================================
# tabs/dashboard/stats_leaders.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from common.widgets.data_grid import DataGrid


class StatsLeadersWindow(QWidget):
    """Window showing statistical leaders"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize stats leaders UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Statistical Leaders")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Stats tabs
        self.stats_tabs = QTabWidget()
        
        # TODO: Add tabs for rushing, passing, receiving, defense, etc.
        
        layout.addWidget(self.stats_tabs)
        
    def load_stats(self):
        """Load statistical leaders"""
        # TODO: Query database for statistical leaders
        pass

