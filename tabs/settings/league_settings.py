# ========================================
# tabs/settings/league_settings.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QFileDialog, QMessageBox)


class LeagueSettingsPanel(QWidget):
    """League basic settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.league_id = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize league settings UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("League Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Basic league info group
        basic_group = QGroupBox("Basic League Information")
        basic_layout = QFormLayout(basic_group)
        
        self.league_name_edit = QLineEdit()
        basic_layout.addRow("League Name:", self.league_name_edit)
        
        self.game_files_path_edit = QLineEdit()
        self.browse_path_btn = QPushButton("Browse...")
        self.browse_path_btn.clicked.connect(self.browse_game_files_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.game_files_path_edit)
        path_layout.addWidget(self.browse_path_btn)
        basic_layout.addRow("Game Files Path:", path_layout)
        
        layout.addWidget(basic_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.reset_btn = QPushButton("Reset to Defaults")
        
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
    def load_settings(self):
        """Load current league settings from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get the current league (assuming single league for now)
            cursor.execute("""
                SELECT league_id, league_name, game_files_path 
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                self.league_id = result['league_id']
                self.league_name_edit.setText(result['league_name'] or "")
                self.game_files_path_edit.setText(result['game_files_path'] or "")
            else:
                # No league found - create default values
                self.league_name_edit.setText("New League")
                self.game_files_path_edit.setText("")
                print("No active league found in database")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading league settings: {str(e)}")
            print(f"Error loading league settings: {e}")
        
    def save_settings(self):
        """Save league settings to database"""
        try:
            league_name = self.league_name_edit.text().strip()
            game_files_path = self.game_files_path_edit.text().strip()
            
            # Validate input
            if not league_name:
                QMessageBox.warning(self, "Validation Error", "League name cannot be empty.")
                return
                
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if self.league_id:
                # Update existing league
                cursor.execute("""
                    UPDATE leagues 
                    SET league_name = ?, game_files_path = ?
                    WHERE league_id = ?
                """, (league_name, game_files_path, self.league_id))
            else:
                # Create new league
                cursor.execute("""
                    INSERT INTO leagues (league_name, game_files_path, created_date, is_active)
                    VALUES (?, ?, DATE('now'), TRUE)
                """, (league_name, game_files_path))
                self.league_id = cursor.lastrowid
            
            conn.commit()
            QMessageBox.information(self, "Success", "League settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error saving league settings: {str(e)}")
            print(f"Error saving league settings: {e}")
        
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
        
    def browse_game_files_path(self):
        """Browse for game files directory"""
        current_path = self.game_files_path_edit.text()
        if not current_path:
            current_path = ""
            
        path = QFileDialog.getExistingDirectory(
            self, 
            "Select Game Files Directory",
            current_path
        )
        
        if path:
            self.game_files_path_edit.setText(path)
