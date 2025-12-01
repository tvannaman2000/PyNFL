# ========================================
# tabs/dashboard/quick_actions.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout


class QuickActionsWindow(QWidget):
    """Window with quick action buttons"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize quick actions UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Quick Actions")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Action buttons grid
        button_layout = QGridLayout()
        
        # Row 1
        self.team_mgmt_btn = QPushButton("Team Management")
        self.player_db_btn = QPushButton("Player Database")
        button_layout.addWidget(self.team_mgmt_btn, 0, 0)
        button_layout.addWidget(self.player_db_btn, 0, 1)
        
        # Row 2
        self.schedule_mgmt_btn = QPushButton("Schedule Management")
        self.export_data_btn = QPushButton("Export League Data")
        button_layout.addWidget(self.schedule_mgmt_btn, 1, 0)
        button_layout.addWidget(self.export_data_btn, 1, 1)
        
        # Row 3
        self.import_results_btn = QPushButton("Import Game Results")
        self.draft_center_btn = QPushButton("Draft Center")
        button_layout.addWidget(self.import_results_btn, 2, 0)
        button_layout.addWidget(self.draft_center_btn, 2, 1)
        
        layout.addLayout(button_layout)
        
        # TODO: Connect button signals to appropriate actions

