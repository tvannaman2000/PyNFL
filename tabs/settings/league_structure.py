# tabs/settings/league_structure.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QPushButton,
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QMessageBox, QDialog, QDialogButtonBox, QLineEdit,
                            QHeaderView)
from PyQt5.QtCore import Qt


class LeagueStructurePanel(QWidget):
    """League structure configuration panel with database integration"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_league_id = None
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize league structure UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("League Structure")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Current structure summary
        summary_group = QGroupBox("Current Structure")
        summary_layout = QFormLayout(summary_group)
        
        self.num_conferences_spin = QSpinBox()
        self.num_conferences_spin.setRange(0, 10)
        self.num_conferences_spin.setValue(0)
        self.num_conferences_spin.setReadOnly(True)
        summary_layout.addRow("Number of Conferences:", self.num_conferences_spin)
        
        self.divisions_per_conf_spin = QSpinBox()
        self.divisions_per_conf_spin.setRange(0, 20)
        self.divisions_per_conf_spin.setValue(0)
        self.divisions_per_conf_spin.setReadOnly(True)
        summary_layout.addRow("Total Divisions:", self.divisions_per_conf_spin)
        
        self.teams_per_div_spin = QSpinBox()
        self.teams_per_div_spin.setRange(0, 50)
        self.teams_per_div_spin.setValue(0)
        self.teams_per_div_spin.setReadOnly(True)
        summary_layout.addRow("Total Teams:", self.teams_per_div_spin)
        
        layout.addWidget(summary_group)
        
        # Conference/Division management
        mgmt_group = QGroupBox("Conference & Division Management")
        mgmt_layout = QVBoxLayout(mgmt_group)
        
        # Table for displaying conferences and divisions
        self.structure_table = QTableWidget()
        self.structure_table.setColumnCount(5)
        self.structure_table.setHorizontalHeaderLabels([
            "Type", "Conference", "Division", "Teams", "Abbreviation"
        ])
        
        # Set minimum height to show more rows initially (roughly 15-20 rows)
        self.structure_table.setMinimumHeight(400)
        
        # Set column widths
        header = self.structure_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Conference
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Division
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Teams
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Abbreviation
        
        self.structure_table.setSelectionBehavior(QTableWidget.SelectRows)
        mgmt_layout.addWidget(self.structure_table)
        
        # Management buttons
        mgmt_button_layout = QHBoxLayout()
        self.add_conference_btn = QPushButton("Add Conference")
        self.add_division_btn = QPushButton("Add Division")
        self.edit_btn = QPushButton("Edit Selected")
        self.delete_btn = QPushButton("Delete Selected")
        self.refresh_btn = QPushButton("Refresh")
        
        # Connect button signals
        self.add_conference_btn.clicked.connect(self.add_conference)
        self.add_division_btn.clicked.connect(self.add_division)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.refresh_btn.clicked.connect(self.load_data)
        
        mgmt_button_layout.addWidget(self.add_conference_btn)
        mgmt_button_layout.addWidget(self.add_division_btn)
        mgmt_button_layout.addWidget(self.edit_btn)
        mgmt_button_layout.addWidget(self.delete_btn)
        mgmt_button_layout.addWidget(self.refresh_btn)
        mgmt_button_layout.addStretch()
        
        mgmt_layout.addLayout(mgmt_button_layout)
        layout.addWidget(mgmt_group)
        
        layout.addStretch()
    
    def load_data(self):
        """Load conference and division data from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get the currently active league - same pattern as league_settings.py
            cursor.execute("""
                SELECT league_id, league_name 
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if not result:
                print("No active league found")
                self.current_league_id = None
                self.structure_table.setRowCount(0)
                return
            
            self.current_league_id = result['league_id']
            print(f"Found active league: {result['league_name']} (ID: {self.current_league_id})")
            
            # Clear table first
            self.structure_table.setRowCount(0)
            
            # Load conferences for this league
            cursor.execute("""
                SELECT conference_id, conference_name, abbreviation
                FROM conferences 
                WHERE league_id = ? AND is_active = TRUE
                ORDER BY conference_name
            """, (self.current_league_id,))
            
            conferences = cursor.fetchall()
            print(f"Found {len(conferences)} conferences")
            
            for conf_row in conferences:
                conf_id = conf_row['conference_id']
                conf_name = conf_row['conference_name']
                conf_abbr = conf_row['abbreviation']
                
                # Add conference row to table
                row_count = self.structure_table.rowCount()
                self.structure_table.insertRow(row_count)
                
                self.structure_table.setItem(row_count, 0, QTableWidgetItem("Conference"))
                self.structure_table.setItem(row_count, 1, QTableWidgetItem(conf_name))
                self.structure_table.setItem(row_count, 2, QTableWidgetItem(""))
                self.structure_table.setItem(row_count, 3, QTableWidgetItem(""))
                self.structure_table.setItem(row_count, 4, QTableWidgetItem(conf_abbr or ""))
                
                # Store conference ID for editing/deleting
                self.structure_table.item(row_count, 0).setData(Qt.UserRole, f"conf_{conf_id}")
                
                # Load divisions for this conference
                cursor.execute("""
                    SELECT division_id, division_name, abbreviation
                    FROM divisions 
                    WHERE conference_id = ? AND is_active = TRUE
                    ORDER BY division_name
                """, (conf_id,))
                
                divisions = cursor.fetchall()
                print(f"  Conference {conf_name}: {len(divisions)} divisions")
                
                for div_row in divisions:
                    div_id = div_row['division_id']
                    div_name = div_row['division_name']
                    div_abbr = div_row['abbreviation']
                    
                    # Count teams in this division
                    cursor.execute("""
                        SELECT COUNT(*) as team_count FROM teams 
                        WHERE division_id = ? AND is_active = TRUE
                    """, (div_id,))
                    
                    team_result = cursor.fetchone()
                    team_count = team_result['team_count'] if team_result else 0
                    
                    # Add division row to table
                    row_count = self.structure_table.rowCount()
                    self.structure_table.insertRow(row_count)
                    
                    self.structure_table.setItem(row_count, 0, QTableWidgetItem("  Division"))
                    self.structure_table.setItem(row_count, 1, QTableWidgetItem(conf_name))
                    self.structure_table.setItem(row_count, 2, QTableWidgetItem(div_name))
                    self.structure_table.setItem(row_count, 3, QTableWidgetItem(str(team_count)))
                    self.structure_table.setItem(row_count, 4, QTableWidgetItem(div_abbr or ""))
                    
                    # Store division ID for editing/deleting
                    self.structure_table.item(row_count, 0).setData(Qt.UserRole, f"div_{div_id}")
            
            # Update summary statistics
            self.update_summary_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading league structure: {str(e)}")
            print(f"Error loading league structure: {e}")
    
    def update_summary_stats(self):
        """Update the summary statistics spinboxes"""
        try:
            if not self.current_league_id:
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Count conferences
            cursor.execute("SELECT COUNT(*) as count FROM conferences WHERE league_id = ? AND is_active = TRUE", (self.current_league_id,))
            conf_result = cursor.fetchone()
            num_conferences = conf_result['count'] if conf_result else 0
            
            # Count total divisions  
            cursor.execute("""
                SELECT COUNT(*) as count FROM divisions d
                JOIN conferences c ON d.conference_id = c.conference_id
                WHERE c.league_id = ? AND d.is_active = TRUE AND c.is_active = TRUE
            """, (self.current_league_id,))
            div_result = cursor.fetchone()
            num_divisions = div_result['count'] if div_result else 0
            
            # Count total teams
            cursor.execute("""
                SELECT COUNT(*) as count FROM teams t
                JOIN divisions d ON t.division_id = d.division_id
                JOIN conferences c ON d.conference_id = c.conference_id
                WHERE c.league_id = ? AND t.is_active = TRUE AND d.is_active = TRUE AND c.is_active = TRUE
            """, (self.current_league_id,))
            team_result = cursor.fetchone()
            num_teams = team_result['count'] if team_result else 0
            
            print(f"Summary stats: {num_conferences} conferences, {num_divisions} divisions, {num_teams} teams")
            
            # Update the spinboxes
            self.num_conferences_spin.setValue(num_conferences)
            self.divisions_per_conf_spin.setValue(num_divisions)
            self.teams_per_div_spin.setValue(num_teams)
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error updating summary stats: {str(e)}")
            print(f"Error updating summary stats: {e}")
    
    def add_conference(self):
        """Add a new conference"""
        dialog = ConferenceDivisionDialog(self, "Add Conference")
        if dialog.exec_() == QDialog.Accepted:
            name, abbr = dialog.get_values()
            
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conferences (league_id, conference_name, abbreviation)
                    VALUES (?, ?, ?)
                """, (self.current_league_id, name, abbr))
                conn.commit()
                QMessageBox.information(self, "Success", "Conference added successfully!")
                self.load_data()  # This will call resizeColumnsToContents()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add conference: {str(e)}")
    
    def add_division(self):
        """Add a new division"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT conference_id, conference_name 
                FROM conferences 
                WHERE league_id = ? AND is_active = TRUE
                ORDER BY conference_name
            """, (self.current_league_id,))
            
            conferences = cursor.fetchall()
            
            if not conferences:
                QMessageBox.warning(self, "Warning", "No conferences exist. Please add a conference first.")
                return
            
            # Convert to list of tuples for the dialog
            conf_list = [(row['conference_id'], row['conference_name']) for row in conferences]
            
            dialog = ConferenceDivisionDialog(self, "Add Division", conf_list)
            if dialog.exec_() == QDialog.Accepted:
                name, abbr, conf_id = dialog.get_values()
                
                cursor.execute("""
                    INSERT INTO divisions (conference_id, division_name, abbreviation)
                    VALUES (?, ?, ?)
                """, (conf_id, name, abbr))
                conn.commit()
                QMessageBox.information(self, "Success", "Division added successfully!")
                self.load_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add division: {str(e)}")
    
    def edit_selected(self):
        """Edit the selected conference or division"""
        current_row = self.structure_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a conference or division to edit.")
            return
        
        # Get the item data to determine if it's a conference or division
        item_data = self.structure_table.item(current_row, 0).data(Qt.UserRole)
        
        if item_data.startswith("conf_"):
            self.edit_conference(int(item_data.replace("conf_", "")))
        elif item_data.startswith("div_"):
            self.edit_division(int(item_data.replace("div_", "")))
    
    def edit_conference(self, conf_id):
        """Edit a conference"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current conference data
            cursor.execute("SELECT conference_name, abbreviation FROM conferences WHERE conference_id = ?", (conf_id,))
            result = cursor.fetchone()
            if not result:
                return
            
            current_name = result['conference_name']
            current_abbr = result['abbreviation']
            
            dialog = ConferenceDivisionDialog(self, "Edit Conference", 
                                            current_name=current_name, 
                                            current_abbr=current_abbr)
            if dialog.exec_() == QDialog.Accepted:
                name, abbr = dialog.get_values()
                
                cursor.execute("""
                    UPDATE conferences 
                    SET conference_name = ?, abbreviation = ?
                    WHERE conference_id = ?
                """, (name, abbr, conf_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Conference updated successfully!")
                self.load_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit conference: {str(e)}")
    
    def edit_division(self, div_id):
        """Edit a division"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current division data
            cursor.execute("""
                SELECT d.division_name, d.abbreviation, d.conference_id, c.conference_name
                FROM divisions d
                JOIN conferences c ON d.conference_id = c.conference_id
                WHERE d.division_id = ?
            """, (div_id,))
            div_result = cursor.fetchone()
            if not div_result:
                return
            
            current_name = div_result['division_name']
            current_abbr = div_result['abbreviation']
            current_conf_id = div_result['conference_id']
            
            # Get all conferences for the dropdown
            cursor.execute("""
                SELECT conference_id, conference_name 
                FROM conferences 
                WHERE league_id = ? AND is_active = TRUE
                ORDER BY conference_name
            """, (self.current_league_id,))
            conferences = cursor.fetchall()
            conf_list = [(row['conference_id'], row['conference_name']) for row in conferences]
            
            dialog = ConferenceDivisionDialog(self, "Edit Division", conf_list,
                                            current_name=current_name,
                                            current_abbr=current_abbr,
                                            current_conf_id=current_conf_id)
            if dialog.exec_() == QDialog.Accepted:
                name, abbr, conf_id = dialog.get_values()
                
                cursor.execute("""
                    UPDATE divisions 
                    SET division_name = ?, abbreviation = ?, conference_id = ?
                    WHERE division_id = ?
                """, (name, abbr, conf_id, div_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Division updated successfully!")
                self.load_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit division: {str(e)}")
    
    def delete_selected(self):
        """Delete the selected conference or division"""
        current_row = self.structure_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a conference or division to delete.")
            return
        
        # Get the item data
        item_data = self.structure_table.item(current_row, 0).data(Qt.UserRole)
        item_name = self.structure_table.item(current_row, 1).text()
        
        # Determine item type
        if item_data.startswith("conf_"):
            item_type = "conference"
        else:
            item_type = "division"
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion",
                                   f"Are you sure you want to delete the {item_type} '{item_name}'?\n\n"
                                   f"This action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                if item_data.startswith("conf_"):
                    conf_id = int(item_data.replace("conf_", ""))
                    cursor.execute("UPDATE conferences SET is_active = FALSE WHERE conference_id = ?", (conf_id,))
                elif item_data.startswith("div_"):
                    div_id = int(item_data.replace("div_", ""))
                    cursor.execute("UPDATE divisions SET is_active = FALSE WHERE division_id = ?", (div_id,))
                
                conn.commit()
                QMessageBox.information(self, "Success", f"{item_type.title()} deleted successfully!")
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete {item_type}: {str(e)}")


class ConferenceDivisionDialog(QDialog):
    """Dialog for adding/editing conferences and divisions"""
    
    def __init__(self, parent, title, conferences=None, current_name="", current_abbr="", current_conf_id=None):
        super().__init__(parent)
        self.conferences = conferences
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Name field
        form_layout = QFormLayout()
        self.name_edit = QLineEdit(current_name)
        form_layout.addRow("Name:", self.name_edit)
        
        # Abbreviation field
        self.abbr_edit = QLineEdit(current_abbr)
        self.abbr_edit.setMaxLength(10)
        form_layout.addRow("Abbreviation:", self.abbr_edit)
        
        # Conference selector (for divisions only)
        self.conf_combo = None
        if conferences:
            self.conf_combo = QComboBox()
            for conf_id, conf_name in conferences:
                self.conf_combo.addItem(conf_name, conf_id)
            
            # Set current selection if editing
            if current_conf_id:
                index = self.conf_combo.findData(current_conf_id)
                if index >= 0:
                    self.conf_combo.setCurrentIndex(index)
            
            form_layout.addRow("Conference:", self.conf_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Focus on name field
        self.name_edit.setFocus()
    
    def get_values(self):
        """Get the entered values"""
        name = self.name_edit.text().strip()
        abbr = self.abbr_edit.text().strip()
        
        if self.conf_combo:
            conf_id = self.conf_combo.currentData()
            return name, abbr, conf_id
        else:
            return name, abbr
