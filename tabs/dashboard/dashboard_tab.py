# ========================================
# tabs/dashboard_tab.py
# Version: 1.4 - Auto-load standings on initialization
# ========================================

"""
Dashboard Tab Module

Main dashboard showing league overview, game results, standings, and statistical leaders.
Now includes power rankings functionality.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QGroupBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .season_progress import SeasonProgressWidget

# Import the schedule file writer, roster file writer, and power rankings
try:
    from utils.schedule_file_writer import ScheduleFileWriter
    from utils.roster_file_writer import RosterFileWriter
    from utils.power_rankings import PowerRankingsCalculator
    from utils.standings_calculator import calculate_division_leaders
except ImportError:
    print("Warning: schedule_file_writer, roster_file_writer, power_rankings, or standings_calculator not found. Create utils files")
    ScheduleFileWriter = None
    RosterFileWriter = None
    PowerRankingsCalculator = None
    calculate_division_leaders = None


class StatisticalLeadersWidget(QWidget):
    """Widget displaying statistical leaders in various categories"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_season = 1
        self.current_week = 1
        self.current_league_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the statistical leaders UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Category selector
        selector_layout = QHBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Rushing Yards", "Passing Yards", "Receiving Yards", 
            "Passing TDs", "Rushing TDs", "Receiving TDs",
            "Interceptions", "Sacks"
        ])
        self.category_combo.currentTextChanged.connect(self.update_stats)
        selector_layout.addWidget(QLabel("Category:"))
        selector_layout.addWidget(self.category_combo)
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Leaders table
        self.leaders_table = QTableWidget()
        self.leaders_table.setColumnCount(4)
        self.leaders_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", "Stats"])
        
        # Set column widths
        header = self.leaders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Rank
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Player
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Team
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Stats
        
        self.leaders_table.setColumnWidth(0, 40)  # Rank
        self.leaders_table.setColumnWidth(2, 60)  # Team
        self.leaders_table.setColumnWidth(3, 60)  # Stats
        
        # Table styling
        self.leaders_table.setAlternatingRowColors(True)
        self.leaders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leaders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.leaders_table.verticalHeader().setVisible(False)
        
        # Set maximum height to fit within group box
        self.leaders_table.setMaximumHeight(120)
        
        layout.addWidget(self.leaders_table)
        
        # Process Stats File button
        self.process_stats_btn = QPushButton("Process Stats File")
        self.process_stats_btn.setToolTip("Process STATS.LOG file to update statistics")
        self.process_stats_btn.clicked.connect(self.process_stats_file)
        self.process_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border: none;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        layout.addWidget(self.process_stats_btn)
        
        # Initial load
        self.update_stats()
    
    def update_week(self, season, week):
        """Update when week changes"""
        self.current_season = season
        self.current_week = week
        self.update_stats()
    
    def update_stats(self):
        """Update statistical leaders display"""
        category = self.category_combo.currentText()
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get active league
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            if not league_result:
                self.show_no_data("No active league")
                return
            
            self.current_league_id = league_result['league_id']
            
            # Get leaders for this category
            leaders_data = self.get_category_leaders(cursor, category)
            
            if not leaders_data:
                self.show_no_data(f"No {category} data available")
                return
            
            # Populate table
            self.populate_leaders_table(leaders_data, category)
            
        except Exception as e:
            self.show_no_data(f"Error: {str(e)}")
            print(f"Error loading stats: {e}")
    
    def get_category_leaders(self, cursor, category):
        """Get leaders for specific category"""
        try:
            if category == "Rushing Yards":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.rushing_yards) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.rushing_yards > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
            
            elif category == "Passing Yards":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.passing_yards) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.passing_yards > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Receiving Yards":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.receiving_yards) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.receiving_yards > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Passing TDs":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.passing_touchdowns) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.passing_touchdowns > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Rushing TDs":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.rushing_touchdowns) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.rushing_touchdowns > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Receiving TDs":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.receiving_touchdowns) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.receiving_touchdowns > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Interceptions":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.interceptions) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.interceptions > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
                
            elif category == "Sacks":
                query = """
                    SELECT p.display_name as player_name, t.abbreviation as team_abbr,
                           SUM(ps.sacks) as total_stat,
                           COUNT(*) as games
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN teams t ON ps.team_id = t.team_id
                    WHERE ps.league_id = ? AND ps.season = ? AND ps.sacks > 0
                    GROUP BY ps.player_id, p.display_name, t.abbreviation
                    ORDER BY total_stat DESC LIMIT 5
                """
            
            else:
                return []
            
            cursor.execute(query, (self.current_league_id, self.current_season))
            return cursor.fetchall()
                
        except Exception as e:
            print(f"[DASHBOARD] ✗ Error getting {category} leaders: {str(e)}")
            return []
    
    def populate_leaders_table(self, leaders_data, category):
        """Populate the leaders table with data"""
        self.leaders_table.setRowCount(len(leaders_data))
        
        for row, leader in enumerate(leaders_data):
            # Rank
            rank_item = QTableWidgetItem(f"{row + 1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.leaders_table.setItem(row, 0, rank_item)
            
            # Player name
            player_item = QTableWidgetItem(leader['player_name'])
            self.leaders_table.setItem(row, 1, player_item)
            
            # Team abbreviation
            team_item = QTableWidgetItem(leader['team_abbr'])
            team_item.setTextAlignment(Qt.AlignCenter)
            self.leaders_table.setItem(row, 2, team_item)
            
            # Stats based on category
            if "Yards" in category:
                stats_text = f"{int(leader['total_stat'])}"
            elif "TDs" in category or category == "Interceptions" or category == "Sacks":
                stats_text = f"{int(leader['total_stat'])}"
            else:
                stats_text = f"{leader['total_stat']}"
                
            stats_item = QTableWidgetItem(stats_text)
            stats_item.setTextAlignment(Qt.AlignCenter)
            self.leaders_table.setItem(row, 3, stats_item)
        
        # Adjust row height
        for row in range(len(leaders_data)):
            self.leaders_table.setRowHeight(row, 20)
    
    def show_no_data(self, message):
        """Show no data message"""
        self.leaders_table.setRowCount(1)
        self.leaders_table.setColumnCount(1)
        self.leaders_table.setHorizontalHeaderLabels([""])
        
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        self.leaders_table.setItem(0, 0, item)
        
        # Reset to normal headers when data is available
        self.leaders_table.setColumnCount(4)
        self.leaders_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", "Stats"])
    
    def process_stats_file(self):
        """Process a stats file and update statistical leaders"""
        try:
            # Get current league ID
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            
            if not league_result:
                QMessageBox.warning(self, "No Active League", 
                                  "No active league found. Please create a league first.")
                return
            
            league_id = league_result['league_id']
            
            # Import and use stats processor
            from utils.stats_processor import StatsProcessor
            
            processor = StatsProcessor(self.db_manager.db_path)
            success = processor.select_and_process_stats_file(
                self, league_id, self.current_season, self.current_week
            )
            
            if success:
                # Refresh the statistical leaders
                self.update_stats()
                QMessageBox.information(self, "Stats Processed", 
                                      "Stats processed successfully! Statistical leaders updated.")
            else:
                QMessageBox.warning(self, "Processing Failed", 
                                  "Failed to process stats file.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing stats file: {str(e)}")


class ThisWeeksGamesWidget(QWidget):
    """Widget showing games for the current week"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_season = 1
        self.current_week = 1
        self.current_league_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the games widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Games table
        self.games_table = QTableWidget()
        self.games_table.setColumnCount(3)
        self.games_table.setHorizontalHeaderLabels([
            "Away Team", "Home Team", "Results"
        ])
        
        # Set column widths
        header = self.games_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Away Team
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Home Team
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        
        # Hide vertical header
        self.games_table.verticalHeader().setVisible(False)
        
        # Set reasonable height
        self.games_table.setMaximumHeight(250)
        
        layout.addWidget(self.games_table)
    
    def update_week(self, season, week):
        """Update the games display for a specific week"""
        self.current_season = season
        self.current_week = week
        self.load_games()
    
    def load_games(self):
        """Load games for the current week from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current league ID
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            if not league_result:
                self.show_no_data("No active league found")
                return
            
            self.current_league_id = league_result['league_id']
            
            # Get games for this week
            cursor.execute("""
                SELECT 
                    g.game_id,
                    g.day_of_week,
                    g.game_time,
                    g.game_status,
                    g.home_score,
                    g.away_score,
                    g.game_notes,
                    home.full_name as home_team,
                    home.abbreviation as home_abbr,
                    away.full_name as away_team,
                    away.abbreviation as away_abbr
                FROM games g
                JOIN teams home ON g.home_team_id = home.team_id
                JOIN teams away ON g.away_team_id = away.team_id
                WHERE g.league_id = ? AND g.season = ? AND g.week = ?
                ORDER BY 
                    CASE g.day_of_week
                        WHEN 'Thursday' THEN 1
                        WHEN 'Friday' THEN 2
                        WHEN 'Saturday' THEN 3
                        WHEN 'Sunday' THEN 4
                        WHEN 'Monday' THEN 5
                        WHEN 'Tuesday' THEN 6
                        WHEN 'Wednesday' THEN 7
                        ELSE 8
                    END,
                    g.game_time
            """, (self.current_league_id, self.current_season, self.current_week))
            
            games = cursor.fetchall()
            
            if not games:
                self.show_no_data(f"No games scheduled for Week {self.current_week}")
                return
            
            # Populate table
            self.games_table.setRowCount(len(games))
            
            for row, game in enumerate(games):
                # Away Team
                away_text = f"{game['away_team']} ({game['away_abbr']})"
                self.games_table.setItem(row, 0, QTableWidgetItem(away_text))
                
                # Home Team  
                home_text = f"{game['home_team']} ({game['home_abbr']})"
                self.games_table.setItem(row, 1, QTableWidgetItem(home_text))
                
                # Status
                status_text = game['game_status'].title()
                if game['game_status'] == 'COMPLETED':
                    status_text = f"{game['away_score']}-{game['home_score']}"
                elif game['game_status'] == 'IN_PROGRESS':
                    status_text = f"LIVE: {game['away_score']}-{game['home_score']}"
                
                self.games_table.setItem(row, 2, QTableWidgetItem(status_text))
            
            # Resize to content
            self.games_table.resizeColumnsToContents()
            
        except Exception as e:
            self.show_no_data(f"Error loading games: {str(e)}")
            print(f"Error loading games: {e}")
    
    def show_no_data(self, message):
        """Show a message when no games are available"""
        self.games_table.setRowCount(1)
        self.games_table.setColumnCount(1)
        self.games_table.setHorizontalHeaderLabels([""])
        
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        self.games_table.setItem(0, 0, item)
        
        # Reset column headers for next load
        self.games_table.setColumnCount(5)
        self.games_table.setHorizontalHeaderLabels([
            "Away Team", "Home Team", "Status"
        ])


class DivisionLeadersWidget(QWidget):
    """Widget showing current division leaders/standings"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_season = 1
        self.current_week = 1
        self.current_league_id = None
        self.init_ui()
        # FIX: Load standings immediately after UI is initialized
        self.load_initial_standings()
    
    def init_ui(self):
        """Initialize the division leaders widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Standings table
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(5)
        self.standings_table.setHorizontalHeaderLabels([
            "Division", "Team", "Record", "Div", "Pct"
        ])
        
        # Set column widths
        header = self.standings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Division
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Team
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Record
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Div Record
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Pct
        
        # Hide vertical header
        self.standings_table.verticalHeader().setVisible(False)
        
        # Set reasonable height
        self.standings_table.setMaximumHeight(220)
        
        layout.addWidget(self.standings_table)

    def load_initial_standings(self):
       """
       FIX: Load standings on initial display
       Gets current league/season info from database and loads standings
       """
       try:
           conn = self.db_manager.get_connection()
           cursor = conn.cursor()
           
           # Get current league and season info
           cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
           league_result = cursor.fetchone()
           if league_result:
               self.current_league_id = league_result['league_id']
               
               # Get current season/week from league
               cursor.execute("""
                   SELECT current_season, current_week 
                   FROM leagues 
                   WHERE league_id = ?
               """, (self.current_league_id,))
               season_result = cursor.fetchone()
               
               if season_result:
                   self.current_season = season_result['current_season']
                   self.current_week = season_result['current_week']
               
               # Load the standings
               self.load_standings()
       except Exception as e:
           print(f"Error in load_initial_standings: {e}")

    
    def update_week(self, season, week):
        """Update the standings for a specific week"""
        self.current_season = season
        self.current_week = week
        self.load_standings()
    
    def load_standings(self):
        """Load division leaders based on games through current week"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current league ID
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            if not league_result:
                self.show_no_data("No active league found")
                return
            
            self.current_league_id = league_result['league_id']
            
            # Calculate standings with tie-breakers
            if not calculate_division_leaders:
                self.show_no_data("Standings calculator not available")
                return
                
            standings = calculate_division_leaders(self.current_league_id, self.current_season, self.db_manager)
            
            if not standings:
                self.show_no_data("No standings data available")
                return
            
            # Populate table - show division leaders only (one per division)
            divisions_shown = set()
            leaders = []
            
            for team in standings:
                if team['division_name'] not in divisions_shown:
                    divisions_shown.add(team['division_name'])
                    leaders.append(team)
            
            self.standings_table.setRowCount(len(leaders))
            
            for row, leader in enumerate(leaders):
                # Division
                self.standings_table.setItem(row, 0, QTableWidgetItem(leader['division_name']))
                
                # Team
                team_text = f"{leader['team_name']} ({leader['abbreviation']})"
                self.standings_table.setItem(row, 1, QTableWidgetItem(team_text))
                
                # Overall Record
                record_text = f"{leader['wins']}-{leader['losses']}"
                if leader['ties'] > 0:
                    record_text += f"-{leader['ties']}"
                self.standings_table.setItem(row, 2, QTableWidgetItem(record_text))
                
                # Division Record
                div_record_text = f"{leader['div_wins']}-{leader['div_losses']}"
                div_item = QTableWidgetItem(div_record_text)
                div_item.setTextAlignment(Qt.AlignCenter)
                self.standings_table.setItem(row, 3, div_item)
                
                # Win Percentage
                pct_text = f"{leader['win_pct']:.3f}"
                pct_item = QTableWidgetItem(pct_text)
                pct_item.setTextAlignment(Qt.AlignCenter)
                self.standings_table.setItem(row, 4, pct_item)
            
            # Resize to content
            self.standings_table.resizeColumnsToContents()
            
        except Exception as e:
            self.show_no_data(f"Error loading standings: {str(e)}")
            print(f"Error loading standings: {e}")
    
    def show_no_data(self, message):
        """Show a message when no standings are available"""
        self.standings_table.setRowCount(1)
        self.standings_table.setColumnCount(1)
        self.standings_table.setHorizontalHeaderLabels([""])
        
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        self.standings_table.setItem(0, 0, item)
        
        # Reset column headers for next load
        self.standings_table.setColumnCount(5)
        self.standings_table.setHorizontalHeaderLabels([
            "Division", "Team", "Record", "Div", "Pct"
        ])


class DashboardTab(QWidget):
    """Enhanced dashboard tab with real schedule and standings data"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        # Initialize schedule file writer
        if ScheduleFileWriter:
            self.schedule_writer = ScheduleFileWriter(db_manager.db_path)
        else:
            self.schedule_writer = None
            
        # Initialize roster file writer
        if RosterFileWriter:
            self.roster_writer = RosterFileWriter(db_manager.db_path)
        else:
            self.roster_writer = None
        
        # Initialize power rankings calculator
        if PowerRankingsCalculator:
            self.power_rankings = PowerRankingsCalculator(db_manager.db_path)
        else:
            self.power_rankings = None
            
        self.init_ui()
        
        # Connect season progress signals to update other widgets
        self.season_progress.week_changed.connect(self.on_week_changed)
    
    def init_ui(self):
        """Initialize the dashboard tab"""
        layout = QVBoxLayout(self)
        
        # Season Progress (with week navigation)
        self.season_progress = SeasonProgressWidget(self.db_manager)
        layout.addWidget(self.season_progress)
        
        # Main dashboard grid
        grid_layout = QGridLayout()
        
        # This Week's Games
        games_group = QGroupBox("This Week's Games")
        games_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        games_group.setMaximumHeight(320)  # Limit height
        games_layout = QVBoxLayout(games_group)
        self.games_widget = ThisWeeksGamesWidget(self.db_manager)
        games_layout.addWidget(self.games_widget)
        grid_layout.addWidget(games_group, 0, 0)
        
        # Division Leaders
        leaders_group = QGroupBox("Division Leaders")
        leaders_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        leaders_group.setMaximumHeight(270)  # Limit height
        leaders_layout = QVBoxLayout(leaders_group)
        self.leaders_widget = DivisionLeadersWidget(self.db_manager)
        leaders_layout.addWidget(self.leaders_widget)
        grid_layout.addWidget(leaders_group, 0, 1)
        
        # Statistical Leaders - Now functional!
        stats_group = QGroupBox("Statistical Leaders")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        stats_group.setMaximumHeight(200)  # Limit height
        stats_layout = QVBoxLayout(stats_group)
        self.stats_widget = StatisticalLeadersWidget(self.db_manager)
        stats_layout.addWidget(self.stats_widget)
        grid_layout.addWidget(stats_group, 1, 0)
        
        # Game Files Management (both schedule and roster files)
        game_files_group = QGroupBox("Game Files")
        game_files_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        game_files_group.setMaximumHeight(220)  # Increased height for three buttons
        game_files_layout = QVBoxLayout(game_files_group)
        
        # Info label
        game_files_info_label = QLabel("Generate game files for current week")
        game_files_info_label.setAlignment(Qt.AlignCenter)
        game_files_info_label.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 5px;")
        game_files_layout.addWidget(game_files_info_label)
        
        # Write schedule file button
        self.write_schedule_btn = QPushButton("Write Schedule File")
        self.write_schedule_btn.setToolTip("Create season.nfl file for current week")
        self.write_schedule_btn.clicked.connect(self.write_schedule_file)
        self.write_schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        if not self.schedule_writer:
            self.write_schedule_btn.setEnabled(False)
            self.write_schedule_btn.setText("Write Schedule File (not available)")
            
        game_files_layout.addWidget(self.write_schedule_btn)
        
        # Update Power Rankings button - NEW!
        self.update_rankings_btn = QPushButton("⚡ Update Power Rankings")
        self.update_rankings_btn.setToolTip("Calculate power rankings from completed games")
        self.update_rankings_btn.clicked.connect(self.update_power_rankings)
        self.update_rankings_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #4A148C;
            }
        """)
        if not self.power_rankings:
            self.update_rankings_btn.setEnabled(False)
            self.update_rankings_btn.setText("⚡ Update Power Rankings (not available)")
        
        game_files_layout.addWidget(self.update_rankings_btn)
        
        # Write roster files button
        self.write_rosters_btn = QPushButton("Write Roster Files")
        self.write_rosters_btn.setToolTip("Create team roster files for current week")
        self.write_rosters_btn.clicked.connect(self.write_roster_files)
        self.write_rosters_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #357a38;
            }
        """)
        if not self.roster_writer:
            self.write_rosters_btn.setEnabled(False)
            self.write_rosters_btn.setText("Write Roster Files (not available)")
            
        game_files_layout.addWidget(self.write_rosters_btn)
        grid_layout.addWidget(game_files_group, 1, 1)
        
        # Recent Activity - Now shows Power Rankings!
        activity_group = QGroupBox("Recent Activity - Power Rankings")
        activity_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        activity_group.setMaximumHeight(200)  # Limit height
        activity_layout = QVBoxLayout(activity_group)
        
        # Power Rankings Table
        self.rankings_table = QTableWidget()
        self.rankings_table.setColumnCount(4)
        self.rankings_table.setHorizontalHeaderLabels(["Rank", "Team", "Rating", "Games"])
        
        # Set column widths
        header = self.rankings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Rank
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Team
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Rating
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Games
        
        self.rankings_table.setColumnWidth(0, 50)
        self.rankings_table.setColumnWidth(2, 80)
        self.rankings_table.setColumnWidth(3, 60)
        
        activity_layout.addWidget(self.rankings_table)
        grid_layout.addWidget(activity_group, 2, 0, 1, 2)  # Span 2 columns
        
        layout.addLayout(grid_layout)
        
        # Initial load
        self.load_initial_data()
    
    def load_initial_data(self):
        """Load initial data for all widgets"""
        season, week = self.season_progress.get_current_season_week()
        self.on_week_changed(season, week)
        
        # Load power rankings
        self.load_power_rankings()
    
    def on_week_changed(self, season, week):
        """Handle week navigation - update all widgets"""
        print(f"Dashboard updating to Season {season}, Week {week}")
        
        # Update games widget
        self.games_widget.update_week(season, week)
        
        # Update division leaders widget
        self.leaders_widget.update_week(season, week)
        
        # Update statistical leaders widget  
        self.stats_widget.update_week(season, week)
    
    def update_power_rankings(self):
        """Handle update power rankings button click"""
        print("[DASHBOARD] ⚡ Update power rankings button clicked!")
        
        if not self.power_rankings:
            QMessageBox.warning(self, "Power Rankings Error", 
                              "Power rankings calculator is not available.")
            return
        
        try:
            # Get current season from season progress widget
            season, _ = self.season_progress.get_current_season_week()
            
            # Update rankings
            success = self.power_rankings.update_all_rankings(season)
            
            if success:
                # Reload the rankings display
                self.load_power_rankings()
                QMessageBox.information(self, "Success", 
                                      f"Power rankings updated successfully for Season {season}")
            else:
                QMessageBox.warning(self, "Error", "Failed to update power rankings")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating power rankings: {str(e)}")
    
    # ========================================
    # dashboard_tab.py - UPDATE THIS METHOD
    # Version: 2.0
    # Path: tabs/dashboard_tab.py
    # ========================================
    
    def load_power_rankings(self):
        """Load and display current power rankings with win % adjustment"""
        if not self.power_rankings:
            return
        
        try:
            # Get current season
            season, _ = self.season_progress.get_current_season_week()
            
            # Get rankings with win percentage adjustment
            rankings = self.power_rankings.get_rankings(limit=10, season=season)
            
            if not rankings:
                self.rankings_table.setRowCount(1)
                self.rankings_table.setColumnCount(1)
                item = QTableWidgetItem("No rankings available - click 'Update Power Rankings'")
                item.setTextAlignment(Qt.AlignCenter)
                self.rankings_table.setItem(0, 0, item)
                return
            
            # Populate rankings table
            self.rankings_table.setRowCount(len(rankings))
            
            for row, team in enumerate(rankings):
                # Rank
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignCenter)
                self.rankings_table.setItem(row, 0, rank_item)
            
                # Team
                team_text = f"{team['full_name']} ({team['abbreviation']})"
                self.rankings_table.setItem(row, 1, QTableWidgetItem(team_text))
                
                # Rating (adjusted)
                rating_item = QTableWidgetItem(f"{team['current_rating']:.0f}")
                rating_item.setTextAlignment(Qt.AlignCenter)
                
                # Add tooltip showing breakdown if available
                if 'win_pct_adjustment' in team:
                    tooltip = f"Base ELO: {team['base_rating']:.0f}\nWin % Adj: {team['win_pct_adjustment']:+.0f}"
                    rating_item.setToolTip(tooltip)
                
                self.rankings_table.setItem(row, 2, rating_item)
                
                # Games
                games_item = QTableWidgetItem(str(team['games_counted']))
                games_item.setTextAlignment(Qt.AlignCenter)
                self.rankings_table.setItem(row, 3, games_item)
            
        except Exception as e:
            print(f"Error loading power rankings: {e}")

    
    def write_schedule_file(self):
        """Handle write schedule file button click"""
        print(f"[DASHBOARD] ✓ Write schedule file button clicked!")
        
        if not self.schedule_writer:
            QMessageBox.warning(self, "Schedule Writer Error", 
                              "Schedule file writer is not available. Please check utils/schedule_file_writer.py")
            return
        
        try:
            # Get current season/week from season progress widget
            season, week = self.season_progress.get_current_season_week()
            
            # Write the schedule file for current week
            success = self.schedule_writer.write_week_schedule_file(season, week)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Schedule file generated successfully for Season {season}, Week {week}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate schedule file")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating schedule file: {str(e)}")
    
    def write_roster_files(self):
        """Handle write roster files button click"""
        print(f"[DASHBOARD] ✓ Write roster files button clicked!")
        
        if not self.roster_writer:
            QMessageBox.warning(self, "Roster Writer Error", 
                              "Roster file writer is not available. Please check utils/roster_file_writer.py")
            return
        
        try:
            # Get current season/week from season progress widget
            season, week = self.season_progress.get_current_season_week()
            
            # Write roster files for current week's teams
            success = self.roster_writer.write_week_roster_files(season, week)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Roster files generated successfully for Season {season}, Week {week}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate roster files")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating roster files: {str(e)}")
