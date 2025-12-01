# ========================================
# tabs/settings/team_management.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QPushButton, QTableWidget, QLineEdit,
                            QComboBox)


class TeamManagementPanel(QWidget):
    """Team management settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize team management UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("Team Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Team search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.team_search_edit = QLineEdit()
        search_layout.addWidget(self.team_search_edit)
        
        search_layout.addWidget(QLabel("Conference:"))
        self.conference_filter = QComboBox()
        search_layout.addWidget(self.conference_filter)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Teams table
        teams_group = QGroupBox("Teams")
        teams_layout = QVBoxLayout(teams_group)
        
        self.teams_table = QTableWidget()
        teams_layout.addWidget(self.teams_table)
        
        # Team management buttons
        team_button_layout = QHBoxLayout()
        self.add_team_btn = QPushButton("Add Team")
        self.edit_team_btn = QPushButton("Edit Team")
        self.delete_team_btn = QPushButton("Delete Team")
        self.import_teams_btn = QPushButton("Import Teams")
        self.export_teams_btn = QPushButton("Export Teams")
        
        team_button_layout.addWidget(self.add_team_btn)
        team_button_layout.addWidget(self.edit_team_btn)
        team_button_layout.addWidget(self.delete_team_btn)
        team_button_layout.addWidget(self.import_teams_btn)
        team_button_layout.addWidget(self.export_teams_btn)
        team_button_layout.addStretch()
        
        teams_layout.addLayout(team_button_layout)
        layout.addWidget(teams_group)
        
        layout.addStretch()

