# ========================================
# pynfl.py - Main Application Entry Point
# Version: 1.1
# Path: pynfl.py
# ========================================

"""
NFL Challenge League Manager - Main Application

Main entry point for the NFL Challenge League Manager application.
Manages the tabbed interface and database connection.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import all tab modules
from tabs.dashboard.dashboard_tab import DashboardTab
from tabs.teams.teams_tab import TeamsTab
from tabs.players.players_tab import PlayersTab
from tabs.schedule.schedule_tab import ScheduleTab
from tabs.standings.standings_tab import StandingsTab
from tabs.draft.draft_tab import DraftTab
from tabs.transactions.transactions_tab import TransactionsTab
from tabs.coaches.coaches_tab import CoachesTab
from tabs.history.history_tab import HistoryTab
from tabs.statistics.statistics_tab import StatisticsTab
from tabs.offseason.offseason_tab import OffseasonTab
from tabs.settings.settings_tab import SettingsTab

from database.connection import DatabaseManager


class NFLManagerApp(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("NFL Challenge League Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Initialize all tabs
        self.init_tabs()
        
        # Set dashboard as default tab
        self.tab_widget.setCurrentIndex(0)
        
    def init_tabs(self):
        """Initialize all application tabs"""
        # Dashboard tab (default)
        self.dashboard_tab = DashboardTab(self.db_manager)
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        
        # Teams tab
        self.teams_tab = TeamsTab(self.db_manager)
        self.tab_widget.addTab(self.teams_tab, "Teams")
        
        # Players tab
        self.players_tab = PlayersTab(self.db_manager)
        self.tab_widget.addTab(self.players_tab, "Players")
        
        # Schedule tab
        self.schedule_tab = ScheduleTab(self.db_manager)
        self.tab_widget.addTab(self.schedule_tab, "Schedule")
        
        # Standings tab
        self.standings_tab = StandingsTab(self.db_manager)
        self.tab_widget.addTab(self.standings_tab, "Standings")
        
        # Draft tab
        self.draft_tab = DraftTab(self.db_manager)
        self.tab_widget.addTab(self.draft_tab, "Draft")
        
        # Transactions tab
        self.transactions_tab = TransactionsTab(self.db_manager)
        self.tab_widget.addTab(self.transactions_tab, "Transactions")
        
        # Coaches tab
        self.coaches_tab = CoachesTab(self.db_manager)
        self.tab_widget.addTab(self.coaches_tab, "Coaches")
        
        # History tab (NEW)
        self.history_tab = HistoryTab(self.db_manager)
        self.tab_widget.addTab(self.history_tab, "History")
        
        # Statistics tab (NEW)
        self.statistics_tab = StatisticsTab(self.db_manager)
        self.tab_widget.addTab(self.statistics_tab, "Statistics")
        
        # Offseason tab (NEW)
        self.offseason_tab = OffseasonTab(self.db_manager)
        self.tab_widget.addTab(self.offseason_tab, "Offseason")
        
        # Settings tab (keep at end)
        self.settings_tab = SettingsTab(self.db_manager)
        self.tab_widget.addTab(self.settings_tab, "Settings")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("NFL Challenge League Manager")
    
    # Create and show main window
    window = NFLManagerApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
