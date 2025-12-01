# ========================================
# tabs/settings/settings_tab.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QListWidget, QStackedWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from .league_settings import LeagueSettingsPanel
from .league_structure import LeagueStructurePanel
from .team_management import TeamManagementPanel
from .season_configuration import SeasonConfigurationPanel
from .roster_settings import RosterSettingsPanel
from .player_development import PlayerDevelopmentPanel
from .draft_settings import DraftSettingsPanel
#from .scoring_statistics import ScoringStatisticsPanel


class SettingsTab(QWidget):
    """Settings and configuration tab with category navigation"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize settings tab UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Settings & Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Main content area - horizontal split
        content_layout = QHBoxLayout()
        
        # Left side - Categories list
        self.categories_list = QListWidget()
        self.categories_list.setMaximumWidth(250)
        self.categories_list.setMinimumWidth(200)
        
        # Add category items
        categories = [
            "League Settings",
            "League Structure", 
            "Team Management",
            "Season Configuration",
            "Roster & Team Settings",
            "Player Development",
            "Draft Settings"
        ]
        
        for category in categories:
            item = QListWidgetItem(category)
            self.categories_list.addItem(item)
        
        # Connect selection change
        self.categories_list.currentRowChanged.connect(self.on_category_changed)
        
        content_layout.addWidget(self.categories_list)
        
        # Right side - Settings panels
        self.settings_stack = QStackedWidget()
        
        # Create all settings panels
        self.league_settings_panel = LeagueSettingsPanel(self.db_manager)
        self.league_structure_panel = LeagueStructurePanel(self.db_manager)
        self.team_management_panel = TeamManagementPanel(self.db_manager)
        self.season_config_panel = SeasonConfigurationPanel(self.db_manager)
        self.roster_settings_panel = RosterSettingsPanel(self.db_manager)
        self.player_dev_panel = PlayerDevelopmentPanel(self.db_manager)
        self.draft_settings_panel = DraftSettingsPanel(self.db_manager)
        # self.scoring_stats_panel = ScoringStatisticsPanel(self.db_manager)
        
        # Add panels to stack
        self.settings_stack.addWidget(self.league_settings_panel)
        self.settings_stack.addWidget(self.league_structure_panel)
        self.settings_stack.addWidget(self.team_management_panel)
        self.settings_stack.addWidget(self.season_config_panel)
        self.settings_stack.addWidget(self.roster_settings_panel)
        self.settings_stack.addWidget(self.player_dev_panel)
        self.settings_stack.addWidget(self.draft_settings_panel)
        #self.settings_stack.addWidget(self.scoring_stats_panel)
        
        content_layout.addWidget(self.settings_stack)
        layout.addLayout(content_layout)
        
        # Set default selection to League Settings (index 0)
        self.categories_list.setCurrentRow(0)
        self.settings_stack.setCurrentIndex(0)
        
    def on_category_changed(self, index):
        """Handle category selection change"""
        if index >= 0:
            self.settings_stack.setCurrentIndex(index)
