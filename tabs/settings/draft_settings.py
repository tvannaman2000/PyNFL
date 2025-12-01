# ========================================
# tabs/settings/draft_settings.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QPushButton, QComboBox, QMessageBox, QLineEdit, 
                            QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt


class DraftSettingsPanel(QWidget):
    """Draft settings configuration panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.league_id = None
        self.config_id = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize draft settings UI"""
        # Main scroll area since we have many controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_widget = QWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        
        # Panel title
        title = QLabel("Draft Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Configuration info
        info_group = QGroupBox("Configuration Info")
        info_layout = QFormLayout(info_group)
        
        self.config_name_edit = QLineEdit()
        self.config_name_edit.setPlaceholderText("e.g., Standard Draft Rules")
        self.config_name_edit.setMinimumWidth(300)
        info_layout.addRow("Configuration Name:", self.config_name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Description of this draft configuration...")
        info_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(info_group)
        
        # Draft structure group
        structure_group = QGroupBox("Draft Structure")
        structure_layout = QFormLayout(structure_group)
        
        self.draft_rounds_spin = QSpinBox()
        self.draft_rounds_spin.setRange(3, 12)
        self.draft_rounds_spin.setValue(7)
        self.draft_rounds_spin.setToolTip("Number of draft rounds")
        structure_layout.addRow("Number of Rounds:", self.draft_rounds_spin)
        
        self.draft_order_combo = QComboBox()
        self.draft_order_combo.addItems([
            "Worst to Best Record",
            "Random Order",
            "Custom Order"
        ])
        self.draft_order_combo.setToolTip("How draft order is determined")
        structure_layout.addRow("Draft Order Method:", self.draft_order_combo)
        
        self.compensatory_picks = QCheckBox("Enable Compensatory Picks")
        self.compensatory_picks.setToolTip("Add compensatory picks at end of rounds")
        structure_layout.addRow("", self.compensatory_picks)
        
        layout.addWidget(structure_group)
        
        # Prospect generation group
        prospects_group = QGroupBox("Prospect Generation")
        prospects_layout = QFormLayout(prospects_group)
        
        self.prospects_per_round_spin = QSpinBox()
        self.prospects_per_round_spin.setRange(5, 20)
        self.prospects_per_round_spin.setValue(10)
        self.prospects_per_round_spin.setToolTip("Average number of prospects generated per round")
        prospects_layout.addRow("Prospects per Round:", self.prospects_per_round_spin)
        
        self.quality_variation_spin = QSpinBox()
        self.quality_variation_spin.setRange(1, 10)
        self.quality_variation_spin.setValue(5)
        self.quality_variation_spin.setToolTip("Variation in prospect quality (1=very consistent, 10=wide variation)")
        prospects_layout.addRow("Quality Variation (1-10):", self.quality_variation_spin)
        
        self.auto_generate_prospects = QCheckBox("Auto-Generate Prospects Each Year")
        self.auto_generate_prospects.setChecked(True)
        self.auto_generate_prospects.setToolTip("Automatically create new draft prospects each season")
        prospects_layout.addRow("", self.auto_generate_prospects)
        
        layout.addWidget(prospects_group)
        
        # Draft rules group
        rules_group = QGroupBox("Draft Rules")
        rules_layout = QFormLayout(rules_group)
        
        self.trading_enabled = QCheckBox("Allow Draft Pick Trading")
        self.trading_enabled.setChecked(True)
        self.trading_enabled.setToolTip("Teams can trade draft picks")
        rules_layout.addRow("", self.trading_enabled)
        
        self.undrafted_fa = QCheckBox("Create Undrafted Free Agents")
        self.undrafted_fa.setChecked(True)
        self.undrafted_fa.setToolTip("Undrafted prospects become free agents")
        rules_layout.addRow("", self.undrafted_fa)
        
        self.draft_timer = QCheckBox("Enable Draft Timer")
        self.draft_timer.setToolTip("Limit time per pick")
        rules_layout.addRow("", self.draft_timer)
        
        self.timer_minutes_spin = QSpinBox()
        self.timer_minutes_spin.setRange(1, 60)
        self.timer_minutes_spin.setValue(5)
        self.timer_minutes_spin.setEnabled(False)  # Enabled when timer checkbox is checked
        self.timer_minutes_spin.setToolTip("Minutes per draft pick")
        rules_layout.addRow("Timer Minutes:", self.timer_minutes_spin)
        
        # Connect timer checkbox to enable/disable minutes spinbox
        self.draft_timer.toggled.connect(self.timer_minutes_spin.setEnabled)
        
        layout.addWidget(rules_group)
        
        # Current draft status group
        status_group = QGroupBox("Current Draft Status")
        status_layout = QFormLayout(status_group)
        
        self.current_draft_year_spin = QSpinBox()
        self.current_draft_year_spin.setRange(1, 100)
        self.current_draft_year_spin.setValue(1)
        self.current_draft_year_spin.setToolTip("Current draft year")
        status_layout.addRow("Current Draft Year:", self.current_draft_year_spin)
        
        self.draft_status_combo = QComboBox()
        self.draft_status_combo.addItems([
            "Not Started",
            "In Progress", 
            "Completed",
            "Paused"
        ])
        self.draft_status_combo.setToolTip("Current status of the draft")
        status_layout.addRow("Draft Status:", self.draft_status_combo)
        
        layout.addWidget(status_group)
        
        # Draft management buttons
        mgmt_group = QGroupBox("Draft Management")
        mgmt_layout = QVBoxLayout(mgmt_group)
        
        mgmt_button_layout = QHBoxLayout()
        
        self.generate_prospects_btn = QPushButton("Generate Prospects for Current Year")
        self.generate_prospects_btn.setToolTip("Create new draft prospects for current draft year")
        self.generate_prospects_btn.clicked.connect(self.generate_prospects)
        mgmt_button_layout.addWidget(self.generate_prospects_btn)
        
        self.generate_draft_order_btn = QPushButton("Generate Draft Order")
        self.generate_draft_order_btn.setToolTip("Create draft order based on current method")
        self.generate_draft_order_btn.clicked.connect(self.generate_draft_order)
        mgmt_button_layout.addWidget(self.generate_draft_order_btn)
        
        mgmt_layout.addLayout(mgmt_button_layout)
        
        mgmt_button_layout2 = QHBoxLayout()
        
        self.clear_draft_btn = QPushButton("Clear Draft Results")
        self.clear_draft_btn.setToolTip("Clear all draft picks (keep prospects)")
        self.clear_draft_btn.clicked.connect(self.clear_draft_results)
        mgmt_button_layout2.addWidget(self.clear_draft_btn)
        
        self.reset_draft_order_btn = QPushButton("Reset Draft Order")
        self.reset_draft_order_btn.setToolTip("Reset draft order to original state")
        self.reset_draft_order_btn.clicked.connect(self.reset_draft_order)
        mgmt_button_layout2.addWidget(self.reset_draft_order_btn)
        
        mgmt_layout.addLayout(mgmt_button_layout2)
        layout.addWidget(mgmt_group)
        
        # Save button
        button_layout = QHBoxLayout()
        self.save_draft_btn = QPushButton("Save Draft Configuration")
        self.save_draft_btn.clicked.connect(self.save_settings)
        self.save_draft_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_draft_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
    def load_settings(self):
        """Load current draft settings from database"""
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
            
            # Try to get existing draft configuration
            cursor.execute("""
                SELECT * FROM draft_configuration 
                WHERE league_id = ? AND is_active = TRUE
                LIMIT 1
            """, (self.league_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Load existing configuration
                self.config_id = result['config_id']
                
                # Configuration info
                self.config_name_edit.setText(result['configuration_name'] or "Standard Draft Rules")
                self.description_edit.setPlainText(result['description'] or "")
                
                # Draft structure
                self.draft_rounds_spin.setValue(result['draft_rounds'])
                
                # Map database values to combo box
                order_method_map = {
                    'WORST_TO_BEST': 0,
                    'RANDOM': 1,
                    'CUSTOM': 2
                }
                self.draft_order_combo.setCurrentIndex(order_method_map.get(result['draft_order_method'], 0))
                
                self.compensatory_picks.setChecked(result['enable_compensatory_picks'])
                
                # Prospect generation
                self.prospects_per_round_spin.setValue(result['prospects_per_round'])
                self.quality_variation_spin.setValue(result['quality_variation'])
                self.auto_generate_prospects.setChecked(result['auto_generate_prospects'])
                
                # Draft rules
                self.trading_enabled.setChecked(result['allow_pick_trading'])
                self.undrafted_fa.setChecked(result['create_undrafted_fa'])
                self.draft_timer.setChecked(result['enable_draft_timer'])
                if result['draft_timer_minutes']:
                    self.timer_minutes_spin.setValue(result['draft_timer_minutes'])
                
                # Current draft status
                if result['current_draft_year']:
                    self.current_draft_year_spin.setValue(result['current_draft_year'])
                
                # Map database status to combo box
                status_map = {
                    'NOT_STARTED': 0,
                    'IN_PROGRESS': 1,
                    'COMPLETED': 2,
                    'PAUSED': 3
                }
                self.draft_status_combo.setCurrentIndex(status_map.get(result['draft_status'], 0))
                
            else:
                # No configuration found - using defaults
                self.config_id = None
                self.config_name_edit.setText("Standard Draft Rules")
                self.description_edit.setPlainText("Default NFL-style draft configuration")
                print("No draft configuration found - using defaults")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading draft settings: {str(e)}")
            print(f"Error loading draft settings: {e}")
    
    def save_settings(self):
        """Save draft settings to database"""
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
            
            # Map combo box values to database values
            order_methods = ['WORST_TO_BEST', 'RANDOM', 'CUSTOM']
            draft_statuses = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PAUSED']
            
            order_method = order_methods[self.draft_order_combo.currentIndex()]
            draft_status = draft_statuses[self.draft_status_combo.currentIndex()]
            
            if self.config_id:
                # Update existing configuration
                cursor.execute("""
                    UPDATE draft_configuration SET
                        configuration_name = ?,
                        description = ?,
                        draft_rounds = ?,
                        draft_order_method = ?,
                        enable_compensatory_picks = ?,
                        prospects_per_round = ?,
                        quality_variation = ?,
                        auto_generate_prospects = ?,
                        allow_pick_trading = ?,
                        create_undrafted_fa = ?,
                        enable_draft_timer = ?,
                        draft_timer_minutes = ?,
                        current_draft_year = ?,
                        draft_status = ?,
                        last_modified = CURRENT_TIMESTAMP
                    WHERE config_id = ?
                """, (
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.draft_rounds_spin.value(),
                    order_method,
                    self.compensatory_picks.isChecked(),
                    self.prospects_per_round_spin.value(),
                    self.quality_variation_spin.value(),
                    self.auto_generate_prospects.isChecked(),
                    self.trading_enabled.isChecked(),
                    self.undrafted_fa.isChecked(),
                    self.draft_timer.isChecked(),
                    self.timer_minutes_spin.value() if self.draft_timer.isChecked() else None,
                    self.current_draft_year_spin.value(),
                    draft_status,
                    self.config_id
                ))
            else:
                # Create new configuration
                cursor.execute("""
                    INSERT INTO draft_configuration (
                        league_id, configuration_name, description,
                        draft_rounds, draft_order_method, enable_compensatory_picks,
                        prospects_per_round, quality_variation, auto_generate_prospects,
                        allow_pick_trading, create_undrafted_fa, enable_draft_timer,
                        draft_timer_minutes, current_draft_year, draft_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.league_id,
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.draft_rounds_spin.value(),
                    order_method,
                    self.compensatory_picks.isChecked(),
                    self.prospects_per_round_spin.value(),
                    self.quality_variation_spin.value(),
                    self.auto_generate_prospects.isChecked(),
                    self.trading_enabled.isChecked(),
                    self.undrafted_fa.isChecked(),
                    self.draft_timer.isChecked(),
                    self.timer_minutes_spin.value() if self.draft_timer.isChecked() else None,
                    self.current_draft_year_spin.value(),
                    draft_status
                ))
                
                self.config_id = cursor.lastrowid
            
            conn.commit()
            QMessageBox.information(self, "Success", "Draft configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error saving draft settings: {str(e)}")
            print(f"Error saving draft settings: {e}")
    
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
    
    def generate_prospects(self):
        """Generate prospects for current draft year"""
        QMessageBox.information(self, "Feature Coming Soon", 
                               "Prospect generation will be implemented in a future update.")
    
    def generate_draft_order(self):
        """Generate draft order based on current method"""
        QMessageBox.information(self, "Feature Coming Soon", 
                               "Draft order generation will be implemented in a future update.")
    
    def clear_draft_results(self):
        """Clear all draft results"""
        reply = QMessageBox.question(
            self, 
            "Clear Draft Results", 
            "Are you sure you want to clear all draft results? This will remove all draft picks but keep prospects.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Feature Coming Soon", 
                                   "Draft clearing will be implemented in a future update.")
    
    def reset_draft_order(self):
        """Reset draft order to original state"""
        reply = QMessageBox.question(
            self, 
            "Reset Draft Order", 
            "Are you sure you want to reset the draft order to its original state?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Feature Coming Soon", 
                                   "Draft order reset will be implemented in a future update.")
