# ========================================
# tabs/draft/draft_tab.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class DraftTab(QWidget):
    """Draft management tab"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize draft tab UI"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Draft Center")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # TODO: Add draft board, prospects, draft history components


