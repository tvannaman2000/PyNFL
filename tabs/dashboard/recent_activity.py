# ========================================
# tabs/dashboard/recent_activity.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget


class RecentActivityWindow(QWidget):
    """Window showing recent league activity"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize recent activity UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Recent League Activity")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Activity list
        self.activity_list = QListWidget()
        layout.addWidget(self.activity_list)
        
        self.load_activity()
        
    def load_activity(self):
        """Load recent transactions and events"""
        # TODO: Query database for recent player_history entries
        pass


