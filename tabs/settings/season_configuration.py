# ========================================
# tabs/settings/season_configuration.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QPushButton, QMessageBox)


class SeasonConfigurationPanel(QWidget):
    """Season configuration settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.league_id = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize season configuration UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("Season Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Season structure group
        season_group = QGroupBox("Season Structure")
        season_layout = QFormLayout(season_group)
        
        self.preseason_games_spin = QSpinBox()
        self.preseason_games_spin.setRange(0, 8)
        self.preseason_games_spin.setValue(4)
        season_layout.addRow("Preseason Games:", self.preseason_games_spin)
        
        self.regular_season_games_spin = QSpinBox()
        self.regular_season_games_spin.setRange(8, 20)
        self.regular_season_games_spin.setValue(17)
        season_layout.addRow("Regular Season Games:", self.regular_season_games_spin)
        
        # Home-Away Division Games checkbox
        self.home_away_division_checkbox = QCheckBox("Home-Away Division Games")
        self.home_away_division_checkbox.setChecked(True)  # Default checked
        self.home_away_division_checkbox.setToolTip("Each team plays division rivals both home and away")
        season_layout.addRow("", self.home_away_division_checkbox)
        
        self.conference_games_spin = QSpinBox()
        self.conference_games_spin.setRange(0, 16)
        self.conference_games_spin.setValue(10)
        self.conference_games_spin.valueChanged.connect(self.update_inter_conference_games)
        season_layout.addRow("Conference Games:", self.conference_games_spin)
        
        self.inter_conference_games_spin = QSpinBox()
        self.inter_conference_games_spin.setRange(0, 16)
        self.inter_conference_games_spin.setValue(4)
        self.inter_conference_games_spin.valueChanged.connect(self.update_conference_games)
        season_layout.addRow("Inter-Conference Games:", self.inter_conference_games_spin)
        
        # Add a label to show total games calculation
        self.total_games_label = QLabel()
        self.total_games_label.setStyleSheet("font-weight: bold; color: #666;")
        season_layout.addRow("Calculated Total:", self.total_games_label)
        
        layout.addWidget(season_group)
        
        # Playoff configuration group
        playoff_group = QGroupBox("Playoff Configuration")
        playoff_layout = QFormLayout(playoff_group)
        
        self.playoff_teams_spin = QSpinBox()
        self.playoff_teams_spin.setRange(4, 16)
        self.playoff_teams_spin.setValue(7)
        playoff_layout.addRow("Playoff Teams per Conference:", self.playoff_teams_spin)
        
        self.playoff_weeks_spin = QSpinBox()
        self.playoff_weeks_spin.setRange(3, 6)
        self.playoff_weeks_spin.setValue(4)
        playoff_layout.addRow("Playoff Weeks:", self.playoff_weeks_spin)
        
        layout.addWidget(playoff_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.save_season_btn = QPushButton("Save Season Configuration")
        self.save_season_btn.clicked.connect(self.save_settings)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_season_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Connect signals to update calculations
        self.regular_season_games_spin.valueChanged.connect(self.update_total_games_display)
        self.home_away_division_checkbox.toggled.connect(self.update_total_games_display)
        self.conference_games_spin.valueChanged.connect(self.update_total_games_display)
        self.inter_conference_games_spin.valueChanged.connect(self.update_total_games_display)
        
    def load_settings(self):
        """Load current season settings from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get the current league
            cursor.execute("""
                SELECT league_id, preseason_games, regular_season_games, 
                       division_games, conference_games, playoff_teams_per_conf, 
                       playoff_weeks
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                self.league_id = result['league_id']
                
                # Load values
                self.preseason_games_spin.setValue(result['preseason_games'] or 4)
                self.regular_season_games_spin.setValue(result['regular_season_games'] or 17)
                
                # Division games: if > 0, assume home-away is enabled
                division_games = result['division_games'] or 6
                self.home_away_division_checkbox.setChecked(division_games > 0)
                
                self.conference_games_spin.setValue(result['conference_games'] or 10)
                self.playoff_teams_spin.setValue(result['playoff_teams_per_conf'] or 7)
                self.playoff_weeks_spin.setValue(result['playoff_weeks'] or 4)
                
                # Calculate inter-conference games
                total_reg_games = result['regular_season_games'] or 17
                conf_games = result['conference_games'] or 10
                div_games = division_games if division_games > 0 else 0
                inter_conf_games = max(0, total_reg_games - conf_games - div_games)
                self.inter_conference_games_spin.setValue(inter_conf_games)
                
            else:
                # No league found - set defaults
                self.league_id = None
                self.set_default_values()
                print("No active league found - using defaults")
                
            self.update_total_games_display()
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading season settings: {str(e)}")
            print(f"Error loading season settings: {e}")
            self.set_default_values()
    
    def set_default_values(self):
        """Set default values for all controls"""
        self.preseason_games_spin.setValue(4)
        self.regular_season_games_spin.setValue(17)
        self.home_away_division_checkbox.setChecked(True)
        self.conference_games_spin.setValue(10)
        self.inter_conference_games_spin.setValue(4)
        self.playoff_teams_spin.setValue(7)
        self.playoff_weeks_spin.setValue(4)
    
    def save_settings(self):
        """Save season settings to database"""
        try:
            if not self.league_id:
                QMessageBox.warning(self, "Error", "No league found to save settings to.")
                return
            
            # Calculate division games value
            division_games = 6 if self.home_away_division_checkbox.isChecked() else 0
            
            # Validate that games add up correctly
            total_calculated = self.calculate_total_games()
            regular_season_input = self.regular_season_games_spin.value()
            
            if total_calculated != regular_season_input:
                reply = QMessageBox.question(
                    self, 
                    "Game Count Mismatch", 
                    f"Your division + conference + inter-conference games ({total_calculated}) "
                    f"don't equal your regular season total ({regular_season_input}).\n\n"
                    f"Do you want to save anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Update league settings
            cursor.execute("""
                UPDATE leagues 
                SET preseason_games = ?,
                    regular_season_games = ?,
                    division_games = ?,
                    conference_games = ?,
                    playoff_teams_per_conf = ?,
                    playoff_weeks = ?
                WHERE league_id = ?
            """, (
                self.preseason_games_spin.value(),
                self.regular_season_games_spin.value(),
                division_games,
                self.conference_games_spin.value(),
                self.playoff_teams_spin.value(),
                self.playoff_weeks_spin.value(),
                self.league_id
            ))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Season configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error saving season settings: {str(e)}")
            print(f"Error saving season settings: {e}")
    
    def reset_settings(self):
        """Reset settings to current database values"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset to the current database values? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_settings()
    
    def update_inter_conference_games(self):
        """Update inter-conference games when conference games change"""
        # Prevent infinite recursion
        if hasattr(self, '_updating_games'):
            return
        
        self._updating_games = True
        try:
            regular_total = self.regular_season_games_spin.value()
            conference_games = self.conference_games_spin.value()
            division_games = 6 if self.home_away_division_checkbox.isChecked() else 0
            
            inter_conference = max(0, regular_total - conference_games - division_games)
            self.inter_conference_games_spin.setValue(inter_conference)
            
        finally:
            delattr(self, '_updating_games')
    
    def update_conference_games(self):
        """Update conference games when inter-conference games change"""
        # Prevent infinite recursion
        if hasattr(self, '_updating_games'):
            return
        
        self._updating_games = True
        try:
            regular_total = self.regular_season_games_spin.value()
            inter_conference_games = self.inter_conference_games_spin.value()
            division_games = 6 if self.home_away_division_checkbox.isChecked() else 0
            
            conference_games = max(0, regular_total - inter_conference_games - division_games)
            self.conference_games_spin.setValue(conference_games)
            
        finally:
            delattr(self, '_updating_games')
    
    def calculate_total_games(self):
        """Calculate total games from components"""
        division_games = 6 if self.home_away_division_checkbox.isChecked() else 0
        conference_games = self.conference_games_spin.value()
        inter_conference_games = self.inter_conference_games_spin.value()
        
        return division_games + conference_games + inter_conference_games
    
    def update_total_games_display(self):
        """Update the calculated total games display"""
        calculated_total = self.calculate_total_games()
        regular_season_input = self.regular_season_games_spin.value()
        
        if calculated_total == regular_season_input:
            self.total_games_label.setText(f"{calculated_total} games ✓")
            self.total_games_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.total_games_label.setText(f"{calculated_total} games (should be {regular_season_input})")
            self.total_games_label.setStyleSheet("font-weight: bold; color: red;")
