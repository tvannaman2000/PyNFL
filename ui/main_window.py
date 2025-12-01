"""
ui/main_window.py
Main Window - Core UI Container with Tab Management
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QMenuBar, QStatusBar, QAction, 
                             QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence

# Import tab modules dynamically to handle missing files gracefully
def safe_import(module_name, class_name):
    """Safely import a module and class, return None if not found"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("PyNFL - League Management")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        
        # Connect database signals
        self.db_manager.league_changed.connect(self.on_league_changed)

    def debug_settings_system(self):
        """Debug the settings system"""
        try:
            from ui.settings.base_settings import BaseSettingsPanel
                
            # Create a test panel
            class TestPanel(BaseSettingsPanel):
                def _save_panel_settings(self):
                    # Test saving
                    self.execute_sql("CREATE TABLE IF NOT EXISTS test_settings (key TEXT, value TEXT)")
                    self.execute_sql("INSERT OR REPLACE INTO test_settings VALUES ('test', 'success')")
                
                def _load_panel_settings(self):
                    result = self.execute_sql("SELECT value FROM test_settings WHERE key='test'", fetch=True)
                    return result[0][0] if result else None
            
            # Test the panel
            test_panel = TestPanel(self.db_manager, "Debug Test")
            
            if test_panel.save_settings():
                QMessageBox.information(self, "Settings Test", "✅ Settings system working correctly!")
            else:
                QMessageBox.warning(self, "Settings Test", "❌ Settings system has issues - check console output")
            
            # Clean up
            try:
                test_panel.execute_sql("DROP TABLE IF EXISTS test_settings")
            except:
                pass
                
        except Exception as e:
            QMessageBox.critical(self, "Debug Error", f"Settings system error:\n\n{e}")
            print(f"Settings debug error: {e}")

        
    def setup_ui(self):
        """Initialize the main UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Initialize tabs
        self.setup_tabs()
        
    def setup_tabs(self):
        """Create and setup all tabs"""
        # Import tab classes dynamically - UPDATED DASHBOARD IMPORT
        DashboardTab = safe_import('ui.tabs.dashboard', 'PyNFLDashboard')  # CHANGED
        TeamsTab = safe_import('ui.tabs.teams_tab', 'TeamsTab')
        PlayersTab = safe_import('ui.tabs.players_tab', 'PlayersTab')
        ScheduleTab = safe_import('ui.tabs.schedule_tab', 'ScheduleTab')
        StandingsTab = safe_import('ui.tabs.standings_tab', 'StandingsTab')
        DraftTab = safe_import('ui.tabs.draft_tab', 'DraftTab')
        TransactionsTab = safe_import('ui.tabs.transactions_tab', 'TransactionsTab')
        SettingsTab = safe_import('ui.tabs.settings_tab', 'SettingsTab')
        
        # Dashboard - main status and overview - UPDATED SECTION
        if DashboardTab:
            self.dashboard_tab = DashboardTab(self.db_manager.db_path)  # CHANGED: Pass db_path
            self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
            
            # ADDED: Connect dashboard signals to main window methods
            self.dashboard_tab.advance_week_requested.connect(self.advance_week)
            self.dashboard_tab.process_results_requested.connect(self.process_results)
            self.dashboard_tab.open_tab_requested.connect(self.switch_to_tab)
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Dashboard (TODO)")
        
        # Teams management
        if TeamsTab:
            self.teams_tab = TeamsTab(self.db_manager)
            self.tab_widget.addTab(self.teams_tab, "Teams")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Teams (TODO)")
        
        # Player management
        if PlayersTab:
            self.players_tab = PlayersTab(self.db_manager)
            self.tab_widget.addTab(self.players_tab, "Players")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Players (TODO)")
        
        # Schedule and games
        if ScheduleTab:
            self.schedule_tab = ScheduleTab(self.db_manager)
            self.tab_widget.addTab(self.schedule_tab, "Schedule")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Schedule (TODO)")
        
        # Standings
        if StandingsTab:
            self.standings_tab = StandingsTab(self.db_manager)
            self.tab_widget.addTab(self.standings_tab, "Standings")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Standings (TODO)")
        
        # Draft management
        if DraftTab:
            self.draft_tab = DraftTab(self.db_manager)
            self.tab_widget.addTab(self.draft_tab, "Draft")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Draft (TODO)")
        
        # Transactions
        if TransactionsTab:
            self.transactions_tab = TransactionsTab(self.db_manager)
            self.tab_widget.addTab(self.transactions_tab, "Transactions")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Transactions (TODO)")
        
        # Settings
        if SettingsTab:
            self.settings_tab = SettingsTab(self.db_manager)
            self.tab_widget.addTab(self.settings_tab, "Settings")
        else:
            placeholder = QWidget()
            self.tab_widget.addTab(placeholder, "Settings (TODO)")
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # New League
        new_action = QAction('&New League...', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_league)
        file_menu.addAction(new_action)
        
        # Open League
        open_action = QAction('&Open League...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_league)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Import/Export
        import_menu = file_menu.addMenu('&Import')
        export_menu = file_menu.addMenu('&Export')
        
        # Import options
        import_rosters = QAction('Roster Files...', self)
        import_rosters.triggered.connect(self.import_rosters)
        import_menu.addAction(import_rosters)
        
        import_results = QAction('Game Results...', self)
        import_results.triggered.connect(self.import_results)
        import_menu.addAction(import_results)
        
        # Export options
        export_rosters = QAction('Export Rosters...', self)
        export_rosters.triggered.connect(self.export_rosters)
        export_menu.addAction(export_rosters)
        
        export_schedule = QAction('Export Schedule...', self)
        export_schedule.triggered.connect(self.export_schedule)
        export_menu.addAction(export_schedule)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Season menu
        season_menu = menubar.addMenu('&Season')
        
        advance_week = QAction('Advance &Week', self)
        advance_week.triggered.connect(self.advance_week)
        season_menu.addAction(advance_week)
        
        process_results = QAction('&Process Results...', self)
        process_results.triggered.connect(self.process_results)
        season_menu.addAction(process_results)
        
        season_menu.addSeparator()
        
        advance_season = QAction('Advance &Season...', self)
        advance_season.triggered.connect(self.advance_season)
        season_menu.addAction(advance_season)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        generate_draft = QAction('Generate &Draft Class...', self)
        generate_draft.triggered.connect(self.generate_draft_class)
        tools_menu.addAction(generate_draft)

        debug_settings = QAction('🔍 Debug Settings System', self)
        debug_settings.triggered.connect(self.debug_settings_system)
        tools_menu.addAction(debug_settings)

        
        retire_players = QAction('Process &Retirements...', self)
        retire_players.triggered.connect(self.process_retirements)
        tools_menu.addAction(retire_players)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Initial status
        self.update_status()
        
    def update_status(self):
        """Update the status bar with current league info"""
        if self.db_manager.current_league:
            league_info = self.db_manager.get_league_info()
            status_text = f"League: {league_info['name']} | Season: {league_info['season']} | Week: {league_info['week']}"
            self.status_bar.showMessage(status_text)
        else:
            self.status_bar.showMessage("No league loaded")
            
    def on_league_changed(self):
        """Handle league change signal"""
        self.update_status()
        # Refresh all tabs that have refresh method
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'refresh'):
                tab.refresh()
    
    # ADDED: New method for dashboard tab switching
    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name"""
        for i in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(i)
            if tab_name in tab_text:  # Match partial name to handle (TODO) tabs
                self.tab_widget.setCurrentIndex(i)
                break
                
    # Menu action handlers
    def new_league(self):
        """Create a new league"""
        # This will open a dialog to create new league
        pass
        
    def open_league(self):
        """Open existing league"""
        pass
        
    def import_rosters(self):
        """Import roster files from NFL Challenge"""
        pass
        
    def import_results(self):
        """Import game results"""
        pass
        
    def export_rosters(self):
        """Export rosters for NFL Challenge"""
        pass
        
    def export_schedule(self):
        """Export schedule files"""
        pass
        
    def advance_week(self):
        """Advance to next week"""
        try:
            if self.db_manager.advance_week():
                self.update_status()
                
                # ADDED: Refresh dashboard if it exists
                if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'refresh_data'):
                    self.dashboard_tab.refresh_data()
                    
                QMessageBox.information(self, "Week Advanced", "Successfully advanced to next week.")
            else:
                QMessageBox.warning(self, "Cannot Advance", "Cannot advance week. Check that current week is complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error advancing week: {e}")
            
    def process_results(self):
        """Process game results for current week"""
        try:
            # Your game results processing logic here
            print("Processing game results...")
            
            # Use your db_manager to update sync timestamp if method exists
            if hasattr(self.db_manager, 'update_sync_timestamp'):
                self.db_manager.update_sync_timestamp()
            
            # ADDED: Refresh dashboard if it exists
            if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'refresh_data'):
                self.dashboard_tab.refresh_data()
                
            # Update status bar
            self.update_status()
            
            QMessageBox.information(self, "Results Processed", "Game results have been processed successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing results: {e}")
        
    def advance_season(self):
        """Advance to next season"""
        pass
        
    def generate_draft_class(self):
        """Generate new draft class"""
        pass
        
    def process_retirements(self):
        """Process player retirements"""
        pass
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About PyNFL", 
                         "PyNFL - League Management Wrapper for NFL Challenge\n\n"
                         "Version 1.0\n"
                         "A comprehensive tool for managing NFL Challenge leagues.")
