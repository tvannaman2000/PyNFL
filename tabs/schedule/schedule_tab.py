# Version: 1.2
# File: tabs/schedule/schedule_tab.py
# ========================================
# tabs/schedule/schedule_tab.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QGroupBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt

# Import the actual generator classes
from .preseason_generator import PreseasonGenerator
from utils.playoff_generator import PlayoffGenerator


class ScheduleTab(QWidget):
    """Schedule management tab"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        print(f"[SCHEDULE_TAB] Initializing with db_manager.db_path: {db_manager.db_path}")
        
        # Create the actual generator instances
        self.preseason_generator = PreseasonGenerator(db_manager.db_path)
        self.playoff_generator = PlayoffGenerator(db_manager)
        
        self.current_league_id = None
        self.current_season = 1
        self.current_week = 1
        self.init_ui()
        self.load_league_info()
        self.load_schedule()
        
        print(f"[SCHEDULE_TAB] ✓ Schedule tab initialization complete!")
        print(f"[SCHEDULE_TAB] Current league ID: {self.current_league_id}")
        print(f"[SCHEDULE_TAB] Preseason generator ready: {self.preseason_generator is not None}")
        print(f"[SCHEDULE_TAB] Playoff generator ready: {self.playoff_generator is not None}")
        
    def init_ui(self):
        """Initialize schedule tab UI"""
        layout = QVBoxLayout(self)
        
        # Title and league info
        header_layout = QVBoxLayout()
        
        title = QLabel("Season Schedule")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0px;")
        header_layout.addWidget(title)
        
        # League info display
        self.league_info_label = QLabel("Loading league information...")
        self.league_info_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        header_layout.addWidget(self.league_info_label)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_group = QGroupBox("Schedule View")
        filter_layout = QHBoxLayout(filter_group)
        
        # Week filter
        filter_layout.addWidget(QLabel("Show Week:"))
        self.week_combo = QComboBox()
        self.week_combo.addItem("All Weeks", "ALL")
        self.week_combo.addItem("Current Week", "CURRENT")
        self.week_combo.currentTextChanged.connect(self.filter_changed)
        filter_layout.addWidget(self.week_combo)
        
        # Game type filter
        filter_layout.addWidget(QLabel("Game Type:"))
        self.game_type_combo = QComboBox()
        self.game_type_combo.addItem("All Games", "ALL")
        self.game_type_combo.addItem("Regular Season", "REGULAR")
        self.game_type_combo.addItem("Preseason", "PRESEASON")
        self.game_type_combo.addItem("Playoffs", "PLAYOFFS")
        self.game_type_combo.currentTextChanged.connect(self.filter_changed)
        filter_layout.addWidget(self.game_type_combo)
        
        filter_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Schedule")
        self.refresh_btn.clicked.connect(self.refresh_schedule)
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(filter_group)
        
        # Schedule management
        mgmt_group = QGroupBox("Schedule Management")
        mgmt_layout = QVBoxLayout(mgmt_group)
        
        # First row of buttons - Generation
        mgmt_row1 = QHBoxLayout()
        
        self.generate_preseason_btn = QPushButton("Generate Preseason")
        self.generate_preseason_btn.setToolTip("Generate preseason schedule for current season")
        self.generate_preseason_btn.clicked.connect(self.generate_preseason)
        mgmt_row1.addWidget(self.generate_preseason_btn)
        
        self.generate_regular_btn = QPushButton("Generate Regular Season")
        self.generate_regular_btn.setToolTip("Generate regular season schedule for current season")
        self.generate_regular_btn.clicked.connect(self.generate_regular_season)
        mgmt_row1.addWidget(self.generate_regular_btn)
        
        mgmt_row1.addStretch()
        mgmt_layout.addLayout(mgmt_row1)
        
        # Second row - Playoff Generation (separate buttons for each round)
        mgmt_row2 = QHBoxLayout()
        mgmt_row2.addWidget(QLabel("Playoffs:"))
        
        self.generate_wildcard_btn = QPushButton("Wild Card")
        self.generate_wildcard_btn.setToolTip("Generate Wild Card round from standings")
        self.generate_wildcard_btn.clicked.connect(self.generate_wildcard)
        mgmt_row2.addWidget(self.generate_wildcard_btn)
        
        self.generate_divisional_btn = QPushButton("Divisional")
        self.generate_divisional_btn.setToolTip("Generate Divisional round placeholders")
        self.generate_divisional_btn.clicked.connect(self.generate_divisional)
        mgmt_row2.addWidget(self.generate_divisional_btn)
        
        self.generate_conf_champ_btn = QPushButton("Conf Champ")
        self.generate_conf_champ_btn.setToolTip("Generate Conference Championship placeholders")
        self.generate_conf_champ_btn.clicked.connect(self.generate_conf_championship)
        mgmt_row2.addWidget(self.generate_conf_champ_btn)
        
        self.generate_championship_btn = QPushButton("Championship")
        self.generate_championship_btn.setToolTip("Generate Championship game placeholder")
        self.generate_championship_btn.clicked.connect(self.generate_championship)
        mgmt_row2.addWidget(self.generate_championship_btn)
        
        mgmt_row2.addStretch()
        mgmt_layout.addLayout(mgmt_row2)
        
        # Third row of buttons - Clear operations
        mgmt_row3 = QHBoxLayout()
        
        self.clear_preseason_btn = QPushButton("Clear Preseason")
        self.clear_preseason_btn.setToolTip("Clear preseason games")
        self.clear_preseason_btn.clicked.connect(self.clear_preseason)
        mgmt_row3.addWidget(self.clear_preseason_btn)
        
        self.clear_regular_btn = QPushButton("Clear Regular Season")
        self.clear_regular_btn.setToolTip("Clear regular season games")
        self.clear_regular_btn.clicked.connect(self.clear_regular_season)
        mgmt_row3.addWidget(self.clear_regular_btn)
        
        self.clear_playoffs_btn = QPushButton("Clear Playoffs")
        self.clear_playoffs_btn.setToolTip("Clear all playoff games")
        self.clear_playoffs_btn.clicked.connect(self.clear_playoffs)
        mgmt_row3.addWidget(self.clear_playoffs_btn)
        
        self.clear_all_btn = QPushButton("Clear All Games")
        self.clear_all_btn.setToolTip("Clear all games for current season")
        self.clear_all_btn.clicked.connect(self.clear_all_games)
        self.clear_all_btn.setStyleSheet("QPushButton { background-color: #ffcccc; }")
        mgmt_row3.addWidget(self.clear_all_btn)
        
        mgmt_row3.addStretch()
        mgmt_layout.addLayout(mgmt_row3)
        
        layout.addWidget(mgmt_group)
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.setup_schedule_table()
        layout.addWidget(self.schedule_table)
        
    def setup_schedule_table(self):
        """Setup the schedule table columns and properties"""
        columns = ["Week", "Game Type", "Away Team", "Home Team", "Score", "Status", "Day", "Notes"]
        self.schedule_table.setColumnCount(len(columns))
        self.schedule_table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Week
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Game Type
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Away Team
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Home Team
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Score
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Day
        header.setSectionResizeMode(7, QHeaderView.Stretch)           # Notes
        
        # Table properties
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setSortingEnabled(True)
        
    def load_league_info(self):
        """Load current league information"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current league info
            cursor.execute("""
                SELECT league_id, league_name, current_season, current_week,
                       regular_season_games, preseason_games, playoff_weeks
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                self.current_league_id = result['league_id']
                self.current_season = result['current_season']
                self.current_week = result['current_week']
                
                # Update info label
                info_text = (f"League: {result['league_name']} | "
                           f"Season {result['current_season']}, Week {result['current_week']} | "
                           f"Regular Season: {result['regular_season_games']} games")
                
                if result['preseason_games']:
                    info_text += f" | Preseason: {result['preseason_games']} games"
                    
                self.league_info_label.setText(info_text)
                
                # Populate week combo with actual weeks
                self.populate_week_combo(result['regular_season_games'], 
                                       result['preseason_games'] or 0,
                                       result['playoff_weeks'] or 4)
                
            else:
                self.league_info_label.setText("No active league found")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading league info: {str(e)}")
            print(f"Error loading league info: {e}")
    
    def populate_week_combo(self, regular_games, preseason_games, playoff_weeks):
        """Populate week combo box with available weeks"""
        # Clear existing items (except "All Weeks" and "Current Week")
        while self.week_combo.count() > 2:
            self.week_combo.removeItem(2)
        
        # Add preseason weeks
        for week in range(1, preseason_games + 1):
            self.week_combo.addItem(f"Preseason Week {week}", f"PRE_{week}")
        
        # Add regular season weeks  
        for week in range(1, regular_games + 1):
            self.week_combo.addItem(f"Week {week}", week)
        
        # Add playoff weeks
        playoff_start_week = regular_games + 1
        for week in range(playoff_start_week, playoff_start_week + playoff_weeks):
            self.week_combo.addItem(f"Playoff Week {week - regular_games}", week)
    
    def load_schedule(self):
        """Load schedule data from database"""
        try:
            if not self.current_league_id:
                return
                
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Build query based on filters
            where_conditions = ["g.league_id = ?", "g.season = ?"]
            params = [self.current_league_id, self.current_season]
            
            # Week filter
            week_filter = self.week_combo.currentData()
            if week_filter == "CURRENT":
                where_conditions.append("g.week = ?")
                params.append(self.current_week)
            elif week_filter not in ["ALL", None] and str(week_filter).startswith("PRE_"):
                # Preseason week
                week_num = int(week_filter.split("_")[1])
                where_conditions.append("g.week = ? AND g.game_type = 'PRESEASON'")
                params.extend([week_num])
            elif week_filter not in ["ALL", None] and isinstance(week_filter, int):
                where_conditions.append("g.week = ?")
                params.append(week_filter)
            
            # Game type filter
            game_type_filter = self.game_type_combo.currentData()
            if game_type_filter == "REGULAR":
                where_conditions.append("g.game_type = 'REGULAR'")
            elif game_type_filter == "PRESEASON":
                where_conditions.append("g.game_type = 'PRESEASON'")
            elif game_type_filter == "PLAYOFFS":
                where_conditions.append("g.game_type IN ('WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL')")
            
            where_clause = " AND ".join(where_conditions)
            
            # Execute query
            query = f"""
                SELECT 
                    g.week,
                    g.game_type,
                    away.full_name as away_team,
                    away.abbreviation as away_abbr,
                    home.full_name as home_team,
                    home.abbreviation as home_abbr,
                    g.away_score,
                    g.home_score,
                    g.game_status,
                    g.day_of_week,
                    g.game_notes,
                    g.playoff_round
                FROM games g
                JOIN teams home ON g.home_team_id = home.team_id
                JOIN teams away ON g.away_team_id = away.team_id
                WHERE {where_clause}
                ORDER BY g.week, g.game_type, g.day_of_week, g.game_id
            """
            
            cursor.execute(query, params)
            games = cursor.fetchall()
            
            # Populate table
            self.populate_schedule_table(games)
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading schedule: {str(e)}")
            print(f"Error loading schedule: {e}")
    
    def populate_schedule_table(self, games):
        """Populate the schedule table with game data"""
        self.schedule_table.setRowCount(len(games))
        
        for row, game in enumerate(games):
            # Week
            week_text = f"Week {game['week']}"
            if game['game_type'] == 'PRESEASON':
                week_text = f"Pre {game['week']}"
            elif game['game_type'] != 'REGULAR':
                if game['playoff_round']:
                    round_names = {1: 'Wild Card', 2: 'Divisional', 3: 'Conference', 4: 'Super Bowl'}
                    week_text = round_names.get(game['playoff_round'], f"Playoff {game['week']}")
            
            self.schedule_table.setItem(row, 0, QTableWidgetItem(week_text))
            
            # Game Type
            game_type = game['game_type'].title() if game['game_type'] else ""
            if game['game_type'] in ['WILDCARD', 'DIVISIONAL', 'CONFERENCE', 'SUPERBOWL']:
                game_type = "Playoff"
            self.schedule_table.setItem(row, 1, QTableWidgetItem(game_type))
            
            # Away Team
            away_team = f"{game['away_team']} ({game['away_abbr']})"
            self.schedule_table.setItem(row, 2, QTableWidgetItem(away_team))
            
            # Home Team  
            home_team = f"{game['home_team']} ({game['home_abbr']})"
            self.schedule_table.setItem(row, 3, QTableWidgetItem(home_team))
            
            # Score
            if game['game_status'] == 'COMPLETED':
                score_text = f"{game['away_score']}-{game['home_score']}"
            elif game['game_status'] == 'IN_PROGRESS':
                score_text = f"{game['away_score']}-{game['home_score']} (Live)"
            else:
                score_text = "Not Played"
            self.schedule_table.setItem(row, 4, QTableWidgetItem(score_text))
            
            # Status
            status_text = game['game_status'].replace('_', ' ').title()
            self.schedule_table.setItem(row, 5, QTableWidgetItem(status_text))
            
            # Day
            day_text = game['day_of_week'] or ""
            self.schedule_table.setItem(row, 6, QTableWidgetItem(day_text))
            
            # Notes
            notes_text = game['game_notes'] or ""
            self.schedule_table.setItem(row, 7, QTableWidgetItem(notes_text))
            
            # Color code rows based on game status
            if game['game_status'] == 'COMPLETED':
                # Light green for completed games
                for col in range(self.schedule_table.columnCount()):
                    item = self.schedule_table.item(row, col)
                    if item:
                        item.setBackground(Qt.lightGray)
            elif game['game_status'] == 'IN_PROGRESS':
                # Light blue for games in progress
                for col in range(self.schedule_table.columnCount()):
                    item = self.schedule_table.item(row, col)
                    if item:
                        item.setBackground(Qt.cyan)
    
    def generate_preseason(self):
        """Generate preseason schedule"""
        print(f"[SCHEDULE_TAB] ✓ Generate preseason button clicked!")
        print(f"[SCHEDULE_TAB] Current league ID: {self.current_league_id}")
        print(f"[SCHEDULE_TAB] Current season: {self.current_season}")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Preseason Schedule",
            f"Generate preseason schedule for Season {self.current_season}?\n\n"
            "This will create all preseason games.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print(f"[SCHEDULE_TAB] ✓ User confirmed - calling preseason generator...")
            
            # Use the correct method name from PreseasonGenerator
            success = self.preseason_generator.generate_schedule(
                self.current_league_id, self.current_season
            )
            
            print(f"[SCHEDULE_TAB] ✓ Preseason generator returned: {success}")
            
            if success:
                QMessageBox.information(self, "Success", "Preseason schedule generated successfully!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to generate preseason schedule")
        else:
            print(f"[SCHEDULE_TAB] User cancelled preseason generation")
    
    def generate_regular_season(self):
        """Generate regular season schedule"""
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        # TODO: Implement regular season generator
        QMessageBox.information(self, "Coming Soon", "Regular season schedule generation will be implemented in a future update.")
    
    def generate_wildcard(self):
        """Generate Wild Card round"""
        print(f"[SCHEDULE_TAB] ✓ Generate Wild Card button clicked!")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Wild Card Round",
            f"Generate Wild Card round for Season {self.current_season}?\n\n"
            "This will create Wild Card games based on current standings.\n"
            "Division winners and wildcards will be seeded.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print(f"[SCHEDULE_TAB] ✓ User confirmed - generating Wild Card round...")
            
            success = self.playoff_generator.generate_wildcard_round(
                self.current_league_id, self.current_season
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                                       "Wild Card round generated successfully!\n\n"
                                       "Games have been scheduled with actual teams based on standings.")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", 
                                   "Failed to generate Wild Card round.\n"
                                   "Check console for details.")
        else:
            print(f"[SCHEDULE_TAB] User cancelled")
    
    def generate_divisional(self):
        """Generate Divisional round"""
        print(f"[SCHEDULE_TAB] ✓ Generate Divisional button clicked!")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Divisional Round",
            f"Generate Divisional round for Season {self.current_season}?\n\n"
            "This will create placeholder games (TBD).\n"
            "Update these after Wild Card games are complete.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.playoff_generator.generate_divisional_round(
                self.current_league_id, self.current_season
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                                       "Divisional round placeholders created!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to generate Divisional round.")
    
    def generate_conf_championship(self):
        """Generate Conference Championship round"""
        print(f"[SCHEDULE_TAB] ✓ Generate Conference Championship button clicked!")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Conference Championships",
            f"Generate Conference Championship games for Season {self.current_season}?\n\n"
            "This will create placeholder games (TBD).",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.playoff_generator.generate_conference_championship(
                self.current_league_id, self.current_season
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                                       "Conference Championship placeholders created!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to generate Conference Championships.")
    
    def generate_championship(self):
        """Generate Championship game"""
        print(f"[SCHEDULE_TAB] ✓ Generate Championship button clicked!")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Championship",
            f"Generate Championship game for Season {self.current_season}?\n\n"
            "This will create a placeholder game (TBD).",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.playoff_generator.generate_superbowl(
                self.current_league_id, self.current_season
            )
            
            if success:
                QMessageBox.information(self, "Success", 
                                       "Championship game placeholder created!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to generate Championship game.")
    
    def clear_preseason(self):
        """Clear preseason games"""
        print(f"[SCHEDULE_TAB] ✓ Clear preseason button clicked!")
        print(f"[SCHEDULE_TAB] Current league ID: {self.current_league_id}")
        print(f"[SCHEDULE_TAB] Current season: {self.current_season}")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Preseason Schedule",
            f"Clear all preseason games for Season {self.current_season}?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print(f"[SCHEDULE_TAB] ✓ User confirmed - calling clear preseason...")
            
            # Use the clear method from PreseasonGenerator
            success = self.preseason_generator.clear_preseason_games(
                self.current_league_id, self.current_season
            )
            
            print(f"[SCHEDULE_TAB] ✓ Clear preseason returned: {success}")
            
            if success:
                QMessageBox.information(self, "Success", "Preseason schedule cleared successfully!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to clear preseason schedule")
        else:
            print(f"[SCHEDULE_TAB] User cancelled clear preseason")
    
    def clear_regular_season(self):
        """Clear regular season games"""
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        # TODO: Implement clear functionality
        QMessageBox.information(self, "Coming Soon", "Clear regular season will be implemented in a future update.")
    
    def clear_playoffs(self):
        """Clear playoff games"""
        print(f"[SCHEDULE_TAB] ✓ Clear playoffs button clicked!")
        print(f"[SCHEDULE_TAB] Current league ID: {self.current_league_id}")
        print(f"[SCHEDULE_TAB] Current season: {self.current_season}")
        
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Playoff Schedule",
            f"Clear all playoff games for Season {self.current_season}?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print(f"[SCHEDULE_TAB] ✓ User confirmed - calling clear playoffs...")
            
            # Use the clear method from PlayoffGenerator
            success = self.playoff_generator.clear_playoff_games(
                self.current_league_id, self.current_season
            )
            
            print(f"[SCHEDULE_TAB] ✓ Clear playoffs returned: {success}")
            
            if success:
                QMessageBox.information(self, "Success", "Playoff schedule cleared successfully!")
                self.refresh_schedule()
            else:
                QMessageBox.critical(self, "Error", "Failed to clear playoff schedule")
        else:
            print(f"[SCHEDULE_TAB] User cancelled clear playoffs")
    
    def clear_all_games(self):
        """Clear all games for current season"""
        if not self.current_league_id:
            QMessageBox.warning(self, "Error", "No active league found")
            return
        
        # TODO: Implement clear functionality
        QMessageBox.information(self, "Coming Soon", "Clear all games will be implemented in a future update.")
    
    def filter_changed(self):
        """Handle filter changes"""
        self.load_schedule()
    
    def refresh_schedule(self):
        """Refresh the schedule display"""
        self.load_league_info()
        self.load_schedule()
