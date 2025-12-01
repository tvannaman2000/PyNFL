# ========================================
# tabs/settings/roster_settings.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QPushButton, QMessageBox, QLineEdit, QTextEdit,
                            QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt


class RosterSettingsPanel(QWidget):
    """Roster and team settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.league_id = None
        self.config_id = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize roster settings UI"""
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
        title = QLabel("Roster & Team Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Configuration info
        info_group = QGroupBox("Configuration Info")
        info_layout = QFormLayout(info_group)
        
        self.config_name_edit = QLineEdit()
        self.config_name_edit.setPlaceholderText("e.g., Standard NFL Rules")
        info_layout.addRow("Configuration Name:", self.config_name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Description of this roster configuration...")
        info_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(info_group)
        
        # Roster sizes group
        sizes_group = QGroupBox("Roster Sizes")
        sizes_layout = QFormLayout(sizes_group)
        
        self.active_roster_spin = QSpinBox()
        self.active_roster_spin.setRange(20, 100)
        self.active_roster_spin.setValue(53)
        sizes_layout.addRow("Active Roster Size:", self.active_roster_spin)
        
        self.injured_reserve_spin = QSpinBox()
        self.injured_reserve_spin.setRange(0, 50)
        self.injured_reserve_spin.setValue(10)
        sizes_layout.addRow("Injured Reserve Size:", self.injured_reserve_spin)
        
        self.practice_squad_spin = QSpinBox()
        self.practice_squad_spin.setRange(0, 30)
        self.practice_squad_spin.setValue(16)
        sizes_layout.addRow("Practice Squad Size:", self.practice_squad_spin)
        
        layout.addWidget(sizes_group)
        
        # Position limits group
        position_group = QGroupBox("Position Requirements")
        position_layout = QGridLayout(position_group)
        
        # Headers
        position_layout.addWidget(QLabel("Position"), 0, 0)
        position_layout.addWidget(QLabel("Minimum"), 0, 1)
        position_layout.addWidget(QLabel("Maximum"), 0, 2)
        
        # Position controls
        positions = [
            ("QB", "Quarterback"),
            ("RB", "Running Back"),
            ("FB", "Fullback"),
            ("WR", "Wide Receiver"),
            ("TE", "Tight End"),
            ("OL", "Offensive Line"),
            ("DL", "Defensive Line"),
            ("LB", "Linebacker"),
            ("DB", "Defensive Back"),
            ("K", "Kicker"),
            ("P", "Punter")
        ]
        
        self.min_spinboxes = {}
        self.max_spinboxes = {}
        
        for row, (pos_code, pos_name) in enumerate(positions, 1):
            # Position label
            pos_label = QLabel(f"{pos_code} ({pos_name})")
            position_layout.addWidget(pos_label, row, 0)
            
            # Minimum spinbox
            min_spin = QSpinBox()
            min_spin.setRange(0, 20)
            min_spin.setValue(self.get_default_min(pos_code))
            self.min_spinboxes[pos_code.lower()] = min_spin
            position_layout.addWidget(min_spin, row, 1)
            
            # Maximum spinbox
            max_spin = QSpinBox()
            max_spin.setRange(0, 30)
            max_spin.setValue(self.get_default_max(pos_code))
            self.max_spinboxes[pos_code.lower()] = max_spin
            position_layout.addWidget(max_spin, row, 2)
            
            # Connect signals to ensure min <= max
            min_spin.valueChanged.connect(lambda v, ms=max_spin, pos=pos_code: self.ensure_min_max(v, ms, pos, True))
            max_spin.valueChanged.connect(lambda v, ms=min_spin, pos=pos_code: self.ensure_min_max(v, ms, pos, False))
        
        layout.addWidget(position_group)
        
        # Roster rules group
        rules_group = QGroupBox("Roster Management Rules")
        rules_layout = QFormLayout(rules_group)
        
        self.allow_position_changes = QCheckBox()
        self.allow_position_changes.setChecked(True)
        self.allow_position_changes.setToolTip("Allow players to change positions")
        rules_layout.addRow("Allow Position Changes:", self.allow_position_changes)
        
        self.require_depth_chart = QCheckBox()
        self.require_depth_chart.setChecked(True)
        self.require_depth_chart.setToolTip("Require depth chart assignments")
        rules_layout.addRow("Require Depth Chart:", self.require_depth_chart)
        
        self.auto_assign_jerseys = QCheckBox()
        self.auto_assign_jerseys.setChecked(False)
        self.auto_assign_jerseys.setToolTip("Automatically assign jersey numbers")
        rules_layout.addRow("Auto-Assign Jersey Numbers:", self.auto_assign_jerseys)
        
        self.enforce_jersey_by_position = QCheckBox()
        self.enforce_jersey_by_position.setChecked(True)
        self.enforce_jersey_by_position.setToolTip("Enforce jersey number ranges by position")
        rules_layout.addRow("Enforce Jersey by Position:", self.enforce_jersey_by_position)
        
        layout.addWidget(rules_group)
        
        # Injury rules group
        injury_group = QGroupBox("Injury & Status Rules")
        injury_layout = QFormLayout(injury_group)
        
        self.max_ir_weeks_spin = QSpinBox()
        self.max_ir_weeks_spin.setRange(1, 52)
        self.max_ir_weeks_spin.setValue(8)
        self.max_ir_weeks_spin.setToolTip("Maximum weeks on IR before forced retirement")
        injury_layout.addRow("Max IR Weeks:", self.max_ir_weeks_spin)
        
        self.allow_ir_return = QCheckBox()
        self.allow_ir_return.setChecked(True)
        self.allow_ir_return.setToolTip("Allow players to return from IR")
        injury_layout.addRow("Allow IR Return:", self.allow_ir_return)
        
        self.max_suspended_weeks_spin = QSpinBox()
        self.max_suspended_weeks_spin.setRange(1, 52)
        self.max_suspended_weeks_spin.setValue(17)
        self.max_suspended_weeks_spin.setToolTip("Maximum suspension length")
        injury_layout.addRow("Max Suspension Weeks:", self.max_suspended_weeks_spin)
        
        layout.addWidget(injury_group)
        
        # Future expansion group (disabled for now)
        future_group = QGroupBox("Future Features (Not Yet Implemented)")
        future_group.setEnabled(False)
        future_layout = QFormLayout(future_group)
        
        self.enable_salary_cap = QCheckBox()
        future_layout.addRow("Enable Salary Cap:", self.enable_salary_cap)
        
        self.salary_cap_spin = QSpinBox()
        self.salary_cap_spin.setRange(0, 999999999)
        self.salary_cap_spin.setValue(200000000)
        future_layout.addRow("Salary Cap Amount:", self.salary_cap_spin)
        
        self.enable_contracts = QCheckBox()
        future_layout.addRow("Enable Contracts:", self.enable_contracts)
        
        layout.addWidget(future_group)
        
        # Save button
        button_layout = QHBoxLayout()
        self.save_roster_btn = QPushButton("Save Roster Configuration")
        self.save_roster_btn.clicked.connect(self.save_settings)
        self.save_roster_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.save_roster_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def get_default_min(self, pos_code):
        """Get default minimum values by position"""
        defaults = {
            'QB': 1, 'RB': 1, 'FB': 0, 'WR': 3, 'TE': 1,
            'OL': 5, 'DL': 4, 'LB': 3, 'DB': 4, 'K': 1, 'P': 1
        }
        return defaults.get(pos_code, 0)
    
    def get_default_max(self, pos_code):
        """Get default maximum values by position"""
        defaults = {
            'QB': 4, 'RB': 8, 'FB': 3, 'WR': 12, 'TE': 6,
            'OL': 15, 'DL': 12, 'LB': 10, 'DB': 12, 'K': 2, 'P': 2
        }
        return defaults.get(pos_code, 5)
    
    def ensure_min_max(self, value, other_spinbox, position, is_min_changing):
        """Ensure minimum <= maximum for position limits"""
        if is_min_changing:
            # Minimum changed, make sure max >= min
            if other_spinbox.value() < value:
                other_spinbox.setValue(value)
        else:
            # Maximum changed, make sure min <= max
            if other_spinbox.value() > value:
                other_spinbox.setValue(value)
    
    def load_settings(self):
        """Load current roster settings from database"""
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
            
            # Try to get existing roster configuration
            cursor.execute("""
                SELECT * FROM roster_configuration 
                WHERE league_id = ? AND is_active = TRUE
                LIMIT 1
            """, (self.league_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Load existing configuration
                self.config_id = result['config_id']
                
                # Configuration info
                self.config_name_edit.setText(result['configuration_name'] or "Standard NFL Rules")
                self.description_edit.setPlainText(result['description'] or "")
                
                # Roster sizes
                self.active_roster_spin.setValue(result['active_roster_size'])
                self.injured_reserve_spin.setValue(result['injured_reserve_size'])
                self.practice_squad_spin.setValue(result['practice_squad_size'])
                
                # Position minimums
                self.min_spinboxes['qb'].setValue(result['min_qb'])
                self.min_spinboxes['rb'].setValue(result['min_rb'])
                self.min_spinboxes['fb'].setValue(result['min_fb'])
                self.min_spinboxes['wr'].setValue(result['min_wr'])
                self.min_spinboxes['te'].setValue(result['min_te'])
                self.min_spinboxes['ol'].setValue(result['min_ol'])
                self.min_spinboxes['dl'].setValue(result['min_dl'])
                self.min_spinboxes['lb'].setValue(result['min_lb'])
                self.min_spinboxes['db'].setValue(result['min_db'])
                self.min_spinboxes['k'].setValue(result['min_k'])
                self.min_spinboxes['p'].setValue(result['min_p'])
                
                # Position maximums
                self.max_spinboxes['qb'].setValue(result['max_qb'])
                self.max_spinboxes['rb'].setValue(result['max_rb'])
                self.max_spinboxes['fb'].setValue(result['max_fb'])
                self.max_spinboxes['wr'].setValue(result['max_wr'])
                self.max_spinboxes['te'].setValue(result['max_te'])
                self.max_spinboxes['ol'].setValue(result['max_ol'])
                self.max_spinboxes['dl'].setValue(result['max_dl'])
                self.max_spinboxes['lb'].setValue(result['max_lb'])
                self.max_spinboxes['db'].setValue(result['max_db'])
                self.max_spinboxes['k'].setValue(result['max_k'])
                self.max_spinboxes['p'].setValue(result['max_p'])
                
                # Rules
                self.allow_position_changes.setChecked(result['allow_position_changes'])
                self.require_depth_chart.setChecked(result['require_depth_chart'])
                self.auto_assign_jerseys.setChecked(result['auto_assign_jersey_numbers'])
                self.enforce_jersey_by_position.setChecked(result['enforce_jersey_by_position'])
                
                # Injury rules
                self.max_ir_weeks_spin.setValue(result['max_ir_weeks'])
                self.allow_ir_return.setChecked(result['allow_ir_return'])
                self.max_suspended_weeks_spin.setValue(result['max_suspended_weeks'])
                
                # Future features
                self.enable_salary_cap.setChecked(result['enable_salary_cap'])
                self.salary_cap_spin.setValue(result['salary_cap_amount'])
                self.enable_contracts.setChecked(result['enable_contracts'])
                
            else:
                # No configuration found - using defaults (already set in init_ui)
                self.config_id = None
                self.config_name_edit.setText("Standard NFL Rules")
                self.description_edit.setPlainText("Default NFL-style roster configuration")
                print("No roster configuration found - using defaults")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading roster settings: {str(e)}")
            print(f"Error loading roster settings: {e}")
    
    def save_settings(self):
        """Save roster settings to database"""
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
                    UPDATE roster_configuration SET
                        configuration_name = ?,
                        description = ?,
                        active_roster_size = ?,
                        injured_reserve_size = ?,
                        practice_squad_size = ?,
                        min_qb = ?, min_rb = ?, min_fb = ?, min_wr = ?, min_te = ?,
                        min_ol = ?, min_dl = ?, min_lb = ?, min_db = ?, min_k = ?, min_p = ?,
                        max_qb = ?, max_rb = ?, max_fb = ?, max_wr = ?, max_te = ?,
                        max_ol = ?, max_dl = ?, max_lb = ?, max_db = ?, max_k = ?, max_p = ?,
                        allow_position_changes = ?,
                        require_depth_chart = ?,
                        auto_assign_jersey_numbers = ?,
                        enforce_jersey_by_position = ?,
                        max_ir_weeks = ?,
                        allow_ir_return = ?,
                        max_suspended_weeks = ?,
                        enable_salary_cap = ?,
                        salary_cap_amount = ?,
                        enable_contracts = ?,
                        last_modified = CURRENT_TIMESTAMP
                    WHERE config_id = ?
                """, (
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.active_roster_spin.value(),
                    self.injured_reserve_spin.value(),
                    self.practice_squad_spin.value(),
                    # Minimums
                    self.min_spinboxes['qb'].value(), self.min_spinboxes['rb'].value(),
                    self.min_spinboxes['fb'].value(), self.min_spinboxes['wr'].value(),
                    self.min_spinboxes['te'].value(), self.min_spinboxes['ol'].value(),
                    self.min_spinboxes['dl'].value(), self.min_spinboxes['lb'].value(),
                    self.min_spinboxes['db'].value(), self.min_spinboxes['k'].value(),
                    self.min_spinboxes['p'].value(),
                    # Maximums
                    self.max_spinboxes['qb'].value(), self.max_spinboxes['rb'].value(),
                    self.max_spinboxes['fb'].value(), self.max_spinboxes['wr'].value(),
                    self.max_spinboxes['te'].value(), self.max_spinboxes['ol'].value(),
                    self.max_spinboxes['dl'].value(), self.max_spinboxes['lb'].value(),
                    self.max_spinboxes['db'].value(), self.max_spinboxes['k'].value(),
                    self.max_spinboxes['p'].value(),
                    # Rules
                    self.allow_position_changes.isChecked(),
                    self.require_depth_chart.isChecked(),
                    self.auto_assign_jerseys.isChecked(),
                    self.enforce_jersey_by_position.isChecked(),
                    # Injury rules
                    self.max_ir_weeks_spin.value(),
                    self.allow_ir_return.isChecked(),
                    self.max_suspended_weeks_spin.value(),
                    # Future features
                    self.enable_salary_cap.isChecked(),
                    self.salary_cap_spin.value(),
                    self.enable_contracts.isChecked(),
                    self.config_id
                ))
            else:
                # Create new configuration
                cursor.execute("""
                    INSERT INTO roster_configuration (
                        league_id, configuration_name, description,
                        active_roster_size, injured_reserve_size, practice_squad_size,
                        min_qb, min_rb, min_fb, min_wr, min_te, min_ol, min_dl, min_lb, min_db, min_k, min_p,
                        max_qb, max_rb, max_fb, max_wr, max_te, max_ol, max_dl, max_lb, max_db, max_k, max_p,
                        allow_position_changes, require_depth_chart, auto_assign_jersey_numbers, enforce_jersey_by_position,
                        max_ir_weeks, allow_ir_return, max_suspended_weeks,
                        enable_salary_cap, salary_cap_amount, enable_contracts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.league_id,
                    config_name,
                    self.description_edit.toPlainText().strip(),
                    self.active_roster_spin.value(),
                    self.injured_reserve_spin.value(),
                    self.practice_squad_spin.value(),
                    # Minimums
                    self.min_spinboxes['qb'].value(), self.min_spinboxes['rb'].value(),
                    self.min_spinboxes['fb'].value(), self.min_spinboxes['wr'].value(),
                    self.min_spinboxes['te'].value(), self.min_spinboxes['ol'].value(),
                    self.min_spinboxes['dl'].value(), self.min_spinboxes['lb'].value(),
                    self.min_spinboxes['db'].value(), self.min_spinboxes['k'].value(),
                    self.min_spinboxes['p'].value(),
                    # Maximums
                    self.max_spinboxes['qb'].value(), self.max_spinboxes['rb'].value(),
                    self.max_spinboxes['fb'].value(), self.max_spinboxes['wr'].value(),
                    self.max_spinboxes['te'].value(), self.max_spinboxes['ol'].value(),
                    self.max_spinboxes['dl'].value(), self.max_spinboxes['lb'].value(),
                    self.max_spinboxes['db'].value(), self.max_spinboxes['k'].value(),
                    self.max_spinboxes['p'].value(),
                    # Rules
                    self.allow_position_changes.isChecked(),
                    self.require_depth_chart.isChecked(),
                    self.auto_assign_jerseys.isChecked(),
                    self.enforce_jersey_by_position.isChecked(),
                    # Injury rules
                    self.max_ir_weeks_spin.value(),
                    self.allow_ir_return.isChecked(),
                    self.max_suspended_weeks_spin.value(),
                    # Future features
                    self.enable_salary_cap.isChecked(),
                    self.salary_cap_spin.value(),
                    self.enable_contracts.isChecked()
                ))
                
                self.config_id = cursor.lastrowid
            
            conn.commit()
            QMessageBox.information(self, "Success", "Roster configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error saving roster settings: {str(e)}")
            print(f"Error saving roster settings: {e}")
    
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
