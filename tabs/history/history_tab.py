# ========================================
# tabs/history/history_tab.py
# Version: 1.0
# Path: tabs/history/history_tab.py
# ========================================

"""
History & Archives Tab Module

Provides access to past seasons, league champions, game archives,
and milestone tracking.

Status: To be implemented
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class HistoryTab(QWidget):
    """History and archives tab - browse past seasons and records"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize history tab UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("History & Archives")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Placeholder message
        placeholder = QLabel("📚 To Be Implemented")
        placeholder.setStyleSheet("""
            font-size: 24px;
            color: #666;
            margin-top: 100px;
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        # Description
        description = QLabel(
            "This tab will contain:\n\n"
            "• Season Archives - Browse past seasons\n"
            "• League Champions - Hall of fame and Super Bowl winners\n"
            "• Game Results Browser - Search completed games with box scores\n"
            "• Season Comparisons - Compare team performance across years\n"
            "• Milestone Tracker - Career records and achievements"
        )
        description.setStyleSheet("""
            font-size: 14px;
            color: #888;
            margin: 20px;
        """)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        layout.addStretch()
