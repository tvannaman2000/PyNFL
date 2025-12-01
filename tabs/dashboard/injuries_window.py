# ========================================
# tabs/dashboard/injuries_window.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from common.widgets.data_grid import DataGrid


class InjuriesWindow(QWidget):
    """Window showing injured players"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize injuries window UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Injuries")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Injuries grid
        self.injuries_grid = DataGrid()
        layout.addWidget(self.injuries_grid)
        
        self.load_injuries()
        
    def load_injuries(self):
        """Load injured players"""
        # TODO: Query database for players on injured reserve
        pass

