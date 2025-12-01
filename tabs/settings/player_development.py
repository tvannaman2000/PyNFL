# ========================================
# tabs/settings/player_development.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QPushButton, QMessageBox,
                            QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt


class PlayerDevelopmentPanel(QWidget):
    """Player development settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.league_id = None
        self.config_id = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize player development UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("Player Development")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Configuration info
        info_group = QGroupBox("Configuration Info")
        info_layout = QFormLayout(info_group)
        
        self.config_name_edit = QLineEdit()
        self.config_name_edit.setPlaceholderText("e.g., Standard Development")
        self.config_name_edit.setMinimumWidth(300)  # Make it wider to prevent cutoff
        info_layout.addRow("Configuration Name:", self.config_name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Description of this development configuration...")
        info_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(info_group)
        
        # Development rates group
        rates_group = QGroupBox("Development Rates")
        rates_layout = QFormLayout(rates_group)
        
        # Add a legend at the top
        legend_label = QLabel("Scale: 1=Very Slow, 3=Slow, 5=Normal, 7=Fast, 10=Very Fast")
        legend_label.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        rates_layout.addRow(legend_label)
        
        # Rookie development - spinbox
        self.rookie_dev_spin = QSpinBox()
        self.rookie_dev_spin.setRange(1, 10)
        self.rookie_dev_spin.setValue(5)
        self.rookie_dev_spin.setToolTip("Development rate for rookie players (1-10)")
        rates_layout.addRow("Rookie Development Rate:", self.rookie_dev_spin)
        
        # Veteran development - spinbox  
        self.veteran_dev_spin = QSpinBox()
        self.veteran_dev_spin.setRange(1, 10)
        self.veteran_dev_spin.setValue(3)
        self.veteran_dev_spin.setToolTip("Development rate for veteran players (1-10)")
        rates_layout.addRow("Veteran Development Rate:", self.veteran_dev_spin)
        
        layout.addWidget(rates_group)
        
        # Age and regression group
        age_group = QGroupBox("Age & Regression")
        age_layout = QFormLayout(age_group)
        
        self.regression_age_spin = QSpinBox()
        self.regression_age_spin.setRange(28, 40)
        self.regression_age_spin.setValue(32)
        self.regression_age_spin.setToolTip("Age when players start to decline")
        age_layout.addRow("Regression Start Age:", self.regression_age_spin)
        
        self.regression_rate_spin = QSpinBox()
        self.regression_rate_spin.setRange(1, 10)
        self.regression_rate_spin.setValue(4)
        self.regression_rate_spin.setToolTip("How fast players decline after regression age (1-10)")
        age_layout.addRow("Regression Rate:", self.regression_rate_spin)
        
        layout.addWidget(age_group)
        
        # Development options group
        options_group = QGroupBox("Development Options")
        options_layout = QVBoxLayout(options_group)
        
        self.position_changes_enabled = QCheckBox("Allow Position Changes")
        self.position_changes_enabled.setChecked(True)
        self.position_changes_enabled.setToolTip("Allow players to change their primary position")
        options_layout.addWidget(self.position_changes_enabled)
        
        self.auto_development = QCheckBox("Automatic Development (per season)")
        self.auto_development.setChecked(True)
        self.auto_development.setToolTip("Automatically develop players each season")
        options_layout.addWidget(self.auto_development)
        
        self.injury_affects_dev = QCheckBox("Injuries Affect Development")
        self.injury_affects_dev.setChecked(True)
        self.injury_affects_dev.setToolTip("Injured players develop slower or not at all")
        options_layout.addWidget(self.injury_affects_dev)
        
        self.playing_time_bonus = QCheckBox("Playing Time Development Bonus")
        self.playing_time_bonus.setChecked(True)
        self.playing_time_bonus.setToolTip("Starters and high-usage players develop faster")
        options_layout.addWidget(self.playing_time_bonus)
        
        layout.addWidget(options_group)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        self.max_skill_increase_spin = QSpinBox()
        self.max_skill_increase_spin.setRange(1, 15)
        self.max_skill_increase_spin.setValue(5)
        self.max_skill_increase_spin.setToolTip("Maximum skill point increase per season")
        advanced_layout.addRow("Max Skill Increase/Season:", self.max_skill_increase_spin)
        
        self.min_skill_decrease_spin = QSpinBox()
        self.min_skill_decrease_spin.setRange(0, 10)
        self.min_skill_decrease_spin.setValue(1)
        self.min_skill_decrease_spin.setToolTip("Minimum skill point decrease during regression")
        advanced_layout.addRow("Min Skill Decrease/Season:", self.min_skill_decrease_spin)
        
        layout.addWidget(advanced_group)
        
        # Save button
        button_layout = QHBoxLayout()
        self.save_dev_btn = QPushButton("Save Development Configuration")
        self.save_dev_btn.clicked.connect(self.save_settings)
        self.save_dev_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_dev_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
    def load_settings(self):
        """Load current player development settings from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get the current league
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            
            if not league_result:
                QMessageBox.warning(self, "Error", "No active league found")
                return
            
            self.league_id = league_result['league_id']
            
            # Try to get existing development configuration
            cursor.execute("""
                SELECT * FROM player_development_config 
                WHERE league_id = ? AND is_active = TRUE
                LIMIT 1
            """, (self.league_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Load existing configuration
                self.config_id = result['config_id']
                
                # Configuration info
                self.config_name_edit.setText(result['configuration_name'] or "Standard Development")
                self.description_edit.setPlainText(result['description'] or "")
                
                # Development rates
                self.rookie_dev_spin.setValue(result['rookie_development_rate'])
                self.veteran_dev_spin.setValue(result['veteran_development_rate'])
                
                # Age and regression
                self.regression_age_spin.setValue(result['regression_start_age'])
                self.regression_rate_spin.setValue(result['regression_rate'])
                
                # Development options
                self.position_changes_enabled.setChecked(result['allow_position_changes'])
                self.auto_development.setChecked(result['automatic_development'])
                self.injury_affects_dev.setChecked(result['injury_affects_development'])
                self.playing_time_bonus.setChecked(result['playing_time_bonus'])
                
                # Advanced settings
                self.max_skill_increase_spin.setValue(result['max_skill_increase_per_season'])
                self.min_skill_decrease_spin.setValue(result['min_skill_decrease_per_season'])
                
            else:
                # No configuration found - using defaults (already set in init_ui)
                self.config_id = None
                self.config_name_edit.setText("Standard Development")
                self.description_edit.setPlainText("Default player development configuration")
                print("No player development configuration found - using defaults")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading development settings: {str(e)}")
            print(f"Error loading development settings: {e}")
    
    def save_settings(self):
        """Save player development settings to database"""
        try:
            if not self.league_id:
                QMessageBox.warning(self, "Error", "No league found to save settings to.")
                return
            
            # Validate that configuration name is not empty
            config_name = self.config_name_edit.text().strip()
            if not config_name:
                QMessageBox.warning(self, "Validation Error", "Configuration name cannot be empty.")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if self.config_id:
                # Update existing configuration
                cursor.execute("""
                    UPDATE player_development_config SET
                        configuration_name = ?,
                        description = ?,
                        rookie_development_rate = ?,
                        veteran_development_rate = ?,
                        regression_start_age = ?,
                        regression_rate = ?,
                        allow_position_changes = ?,
                        automatic_development = ?,
                        injury_affects_development = ?,
                        playing_time_bonus = ?,
                        max_skill_increase_per_season = ?,
                        min_skill_decrease_per_season = ?,
                        last_modified = CURRENT_TIMESTAMP
                    WHERE config_id = ?
                """, (
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.rookie_dev_spin.value(),
                    self.veteran_dev_spin.value(),
                    self.regression_age_spin.value(),
                    self.regression_rate_spin.value(),
                    self.position_changes_enabled.isChecked(),
                    self.auto_development.isChecked(),
                    self.injury_affects_dev.isChecked(),
                    self.playing_time_bonus.isChecked(),
                    self.max_skill_increase_spin.value(),
                    self.min_skill_decrease_spin.value(),
                    self.config_id
                ))
            else:
                # Create new configuration
                cursor.execute("""
                    INSERT INTO player_development_config (
                        league_id, configuration_name, description,
                        rookie_development_rate, veteran_development_rate,
                        regression_start_age, regression_rate,
                        allow_position_changes, automatic_development,
                        injury_affects_development, playing_time_bonus,
                        max_skill_increase_per_season, min_skill_decrease_per_season
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.league_id,
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.rookie_dev_spin.value(),
                    self.veteran_dev_spin.value(),
                    self.regression_age_spin.value(),
                    self.regression_rate_spin.value(),
                    self.position_changes_enabled.isChecked(),
                    self.auto_development.isChecked(),
                    self.injury_affects_dev.isChecked(),
                    self.playing_time_bonus.isChecked(),
                    self.max_skill_increase_spin.value(),
                    self.min_skill_decrease_spin.value()
                ))
                
                self.config_id = cursor.lastrowid
            
            conn.commit()
            QMessageBox.information(self, "Success", "Player development configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error saving development settings: {str(e)}")
            print(f"Error saving development settings: {e}")
    
    def reset_settings(self):
        """Reset settings to current database values or defaults"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset to the current database values? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_settings()
