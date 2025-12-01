# ========================================
# tabs/players/players_tab.py
# Version: 1.2 - Fixed top margin alignment
# Path: tabs/players/players_tab.py
# ========================================

"""
Players Tab Module

Displays searchable/filterable player database with team selection and
detailed player information panel.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QGroupBox, QHeaderView, QMessageBox,
                            QLineEdit, QSplitter, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class PlayersTab(QWidget):
    """Players management tab with team filtering and player details"""
    
    # Position color coding
    POSITION_COLORS = {
        'QB': '#FF6B6B',  # Red
        'RB': '#4ECDC4',  # Teal
        'FB': '#4ECDC4',
        'WR': '#95E77D',  # Green
        'TE': '#FFE66D',  # Yellow
        'C': '#A8E6CF',   # Light green
        'OL': '#A8E6CF',
        'LT': '#A8E6CF',
        'LG': '#A8E6CF',
        'RG': '#A8E6CF',
        'RT': '#A8E6CF',
        'DE': '#FF9999',  # Light red
        'DT': '#FF9999',
        'NT': '#FF9999',
        'LB': '#FFB6C1',  # Pink
        'OLB': '#FFB6C1',
        'ILB': '#FFB6C1',
        'CB': '#B19CD9',  # Purple
        'SS': '#B19CD9',
        'FS': '#B19CD9',
        'DB': '#B19CD9',
        'K': '#FFA07A',   # Orange
        'P': '#FFA07A',
    }
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_league_id = None
        self.current_season = 1
        self.selected_player_id = None
        self.init_ui()
        self.load_league_info()
        self.load_teams()
        
    def init_ui(self):
        """Initialize players tab UI"""
        layout = QVBoxLayout(self)
        # FIXED: Remove explicit margins/spacing - let Qt handle it naturally
        
        # Title
        title = QLabel("Player Database")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create splitter for left panel (filters/list) and right panel (details)
        splitter = QSplitter(Qt.Horizontal)
        
        # ========== LEFT PANEL: Filters and Player List ==========
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)
        left_layout.setSpacing(5)
        
        # Filters group
        filters_group = QGroupBox("Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        # Team filter
        team_layout = QHBoxLayout()
        team_layout.addWidget(QLabel("Team:"))
        self.team_combo = QComboBox()
        self.team_combo.currentIndexChanged.connect(self.filter_players)
        team_layout.addWidget(self.team_combo)
        filters_layout.addLayout(team_layout)
        
        # Position filter
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        self.position_combo = QComboBox()
        self.position_combo.addItem("All Positions", None)
        self.position_combo.currentIndexChanged.connect(self.filter_players)
        position_layout.addWidget(self.position_combo)
        filters_layout.addLayout(position_layout)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Player name...")
        self.search_box.textChanged.connect(self.filter_players)
        search_layout.addWidget(self.search_box)
        filters_layout.addLayout(search_layout)
        
        left_layout.addWidget(filters_group)
        
        # Player count label
        self.player_count_label = QLabel("Players: 0")
        self.player_count_label.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        left_layout.addWidget(self.player_count_label)
        
        # Players table
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(3)
        self.players_table.setHorizontalHeaderLabels(["Name", "Pos", "OVR"])
        
        # Set column widths
        header = self.players_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.Fixed)     # Position
        header.setSectionResizeMode(2, QHeaderView.Fixed)     # Overall
        self.players_table.setColumnWidth(1, 50)
        self.players_table.setColumnWidth(2, 50)
        
        # Hide vertical header
        self.players_table.verticalHeader().setVisible(False)
        
        # Enable selection
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setSelectionMode(QTableWidget.SingleSelection)
        self.players_table.itemSelectionChanged.connect(self.player_selected)
        
        # Enable sorting
        self.players_table.setSortingEnabled(True)
        
        left_layout.addWidget(self.players_table)
        
        # ========== RIGHT PANEL: Player Details ==========
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Details header
        details_header = QLabel("Player Details")
        details_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(details_header)
        
        # Empty state label
        self.empty_state_label = QLabel("← Select a player to view details")
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("color: #999; font-size: 12px;")
        right_layout.addWidget(self.empty_state_label)
        
        # Player details widget (initially hidden)
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        
        # Player name and position
        self.player_name_label = QLabel()
        self.player_name_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        self.details_layout.addWidget(self.player_name_label)
        
        self.player_position_label = QLabel()
        self.player_position_label.setStyleSheet("font-size: 13px; color: #666; margin-bottom: 15px;")
        self.details_layout.addWidget(self.player_position_label)
        
        # Physical attributes group
        physical_group = QGroupBox("Physical Attributes")
        physical_layout = QGridLayout(physical_group)
        physical_layout.setColumnStretch(1, 1)
        
        self.height_label = QLabel()
        self.weight_label = QLabel()
        self.age_label = QLabel()
        self.speed_label = QLabel()
        
        physical_layout.addWidget(QLabel("Height:"), 0, 0)
        physical_layout.addWidget(self.height_label, 0, 1)
        physical_layout.addWidget(QLabel("Weight:"), 1, 0)
        physical_layout.addWidget(self.weight_label, 1, 1)
        physical_layout.addWidget(QLabel("Age:"), 2, 0)
        physical_layout.addWidget(self.age_label, 2, 1)
        physical_layout.addWidget(QLabel("40-Time:"), 3, 0)
        physical_layout.addWidget(self.speed_label, 3, 1)
        
        self.details_layout.addWidget(physical_group)
        
        # Skills group
        skills_group = QGroupBox("Skills & Ratings")
        skills_layout = QGridLayout(skills_group)
        skills_layout.setColumnStretch(1, 1)
        
        self.overall_label = QLabel()
        self.run_label = QLabel()
        self.pass_label = QLabel()
        self.receive_label = QLabel()
        self.block_label = QLabel()
        self.kick_label = QLabel()
        
        skills_layout.addWidget(QLabel("Overall:"), 0, 0)
        skills_layout.addWidget(self.overall_label, 0, 1)
        skills_layout.addWidget(QLabel("Run:"), 1, 0)
        skills_layout.addWidget(self.run_label, 1, 1)
        skills_layout.addWidget(QLabel("Pass:"), 2, 0)
        skills_layout.addWidget(self.pass_label, 2, 1)
        skills_layout.addWidget(QLabel("Receive:"), 3, 0)
        skills_layout.addWidget(self.receive_label, 3, 1)
        skills_layout.addWidget(QLabel("Block:"), 4, 0)
        skills_layout.addWidget(self.block_label, 4, 1)
        skills_layout.addWidget(QLabel("Kick:"), 5, 0)
        skills_layout.addWidget(self.kick_label, 5, 1)
        
        self.details_layout.addWidget(skills_group)
        
        # Career info group
        career_group = QGroupBox("Career Information")
        career_layout = QGridLayout(career_group)
        career_layout.setColumnStretch(1, 1)
        
        self.team_label = QLabel()
        self.jersey_label = QLabel()
        self.experience_label = QLabel()
        self.status_label = QLabel()
        
        career_layout.addWidget(QLabel("Team:"), 0, 0)
        career_layout.addWidget(self.team_label, 0, 1)
        career_layout.addWidget(QLabel("Jersey:"), 1, 0)
        career_layout.addWidget(self.jersey_label, 1, 1)
        career_layout.addWidget(QLabel("Experience:"), 2, 0)
        career_layout.addWidget(self.experience_label, 2, 1)
        career_layout.addWidget(QLabel("Status:"), 3, 0)
        career_layout.addWidget(self.status_label, 3, 1)
        
        self.details_layout.addWidget(career_group)
        
        self.details_widget.setVisible(False)
        
        right_layout.addWidget(self.details_widget)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 35)  # Left panel 35%
        splitter.setStretchFactor(1, 65)  # Right panel 65%
        
        # FIXED: Add stretch of 1 so splitter takes available space
        layout.addWidget(splitter, 1)
    
    def load_league_info(self):
        """Load current league information"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT league_id, current_season 
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                self.current_league_id = result['league_id']
                self.current_season = result['current_season']
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Error loading league info: {str(e)}")
    
    def load_teams(self):
        """Load teams into team filter dropdown"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Clear existing items
            self.team_combo.clear()
            
            # Add "All Teams" and "Free Agents" options
            self.team_combo.addItem("All Teams", None)
            self.team_combo.addItem("Free Agents", 'FREE_AGENT')
            
            # Load teams from database
            if self.current_league_id:
                cursor.execute("""
                    SELECT team_id, full_name, abbreviation
                    FROM teams
                    WHERE league_id = ?
                    ORDER BY full_name
                """, (self.current_league_id,))
                
                teams = cursor.fetchall()
                for team in teams:
                    self.team_combo.addItem(
                        f"{team['full_name']} ({team['abbreviation']})",
                        team['team_id']
                    )
            
            # Load positions
            self.load_positions()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Error loading teams: {str(e)}")
    
    def load_positions(self):
        """Load all positions into position filter"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT position_code
                FROM positions
                ORDER BY position_code
            """)
            
            positions = cursor.fetchall()
            for pos in positions:
                self.position_combo.addItem(pos['position_code'], pos['position_code'])
                
        except Exception as e:
            print(f"Error loading positions: {e}")
    
    def filter_players(self):
        """Filter players based on current selections"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get filter values
            team_filter = self.team_combo.currentData()
            position_filter = self.position_combo.currentData()
            search_text = self.search_box.text().strip()
            
            # Build query based on filters
            if team_filter == 'FREE_AGENT':
                # Free agents query
                query = """
                    SELECT DISTINCT
                        p.player_id,
                        p.first_name || ' ' || p.last_name as player_name,
                        pos.position_code as position,
                        p.overall_rating
                    FROM players p
                    JOIN positions pos ON p.position_id = pos.position_id
                    WHERE p.league_id = ?
                      AND p.player_status = 'ACTIVE'
                      AND p.player_id NOT IN (
                          SELECT player_id FROM roster WHERE is_active = TRUE
                      )
                """
                params = [self.current_league_id]
                
            elif team_filter is None:
                # All teams query - use DISTINCT to avoid duplicates
                query = """
                    SELECT DISTINCT
                        p.player_id,
                        p.first_name || ' ' || p.last_name as player_name,
                        pos.position_code as position,
                        p.overall_rating,
                        (SELECT r2.jersey_number FROM roster r2 
                         WHERE r2.player_id = p.player_id AND r2.is_active = TRUE 
                         LIMIT 1) as jersey_number,
                        COALESCE((SELECT t2.abbreviation FROM roster r2 
                                  JOIN teams t2 ON r2.team_id = t2.team_id 
                                  WHERE r2.player_id = p.player_id AND r2.is_active = TRUE 
                                  LIMIT 1), 'FA') as team_name
                    FROM players p
                    JOIN positions pos ON p.position_id = pos.position_id
                    WHERE p.league_id = ?
                      AND p.player_status = 'ACTIVE'
                """
                params = [self.current_league_id]
                
            else:
                # Specific team query - add DISTINCT to avoid duplicates from multi-position players
                query = """
                    SELECT DISTINCT
                        p.player_id,
                        p.first_name || ' ' || p.last_name as player_name,
                        pos.position_code as position,
                        p.overall_rating,
                        (SELECT r2.jersey_number FROM roster r2 
                         WHERE r2.player_id = p.player_id AND r2.is_active = TRUE 
                           AND r2.team_id = ?
                         LIMIT 1) as jersey_number,
                        t.abbreviation as team_name
                    FROM players p
                    JOIN positions pos ON p.position_id = pos.position_id
                    JOIN roster r ON p.player_id = r.player_id
                    JOIN teams t ON r.team_id = t.team_id
                    WHERE p.league_id = ?
                      AND r.is_active = TRUE
                      AND r.team_id = ?
                      AND p.player_status = 'ACTIVE'
                """
                params = [team_filter, self.current_league_id, team_filter]
            
            # Add position filter
            if position_filter:
                query += " AND pos.position_code = ?"
                params.append(position_filter)
            
            # Add search filter
            if search_text:
                query += " AND (p.first_name || ' ' || p.last_name) LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY player_name"
            
            cursor.execute(query, params)
            players = cursor.fetchall()
            
            # Populate table
            self.populate_players_table(players)
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Error filtering players: {str(e)}")
            print(f"SQL Error: {e}")
    
    def populate_players_table(self, players):
        """Populate the players table with data"""
        # Disable sorting while updating
        self.players_table.setSortingEnabled(False)
        
        # Clear existing rows
        self.players_table.setRowCount(0)
        
        # Add player rows
        for row_idx, player in enumerate(players):
            self.players_table.insertRow(row_idx)
            
            # Store player_id in first column as user data
            name_item = QTableWidgetItem(player['player_name'])
            name_item.setData(Qt.UserRole, player['player_id'])
            self.players_table.setItem(row_idx, 0, name_item)
            
            # Position with color coding
            pos_item = QTableWidgetItem(player['position'])
            pos_item.setTextAlignment(Qt.AlignCenter)
            
            # Apply position color
            pos_code = player['position']
            if pos_code in self.POSITION_COLORS:
                color = QColor(self.POSITION_COLORS[pos_code])
                pos_item.setBackground(color)
            
            self.players_table.setItem(row_idx, 1, pos_item)
            
            # Overall rating
            ovr_item = QTableWidgetItem(str(player['overall_rating']))
            ovr_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code overall rating
            ovr = player['overall_rating']
            if ovr >= 90:
                ovr_item.setForeground(QColor('#2E7D32'))  # Dark green
            elif ovr >= 80:
                ovr_item.setForeground(QColor('#1976D2'))  # Blue
            elif ovr >= 70:
                ovr_item.setForeground(QColor('#F57C00'))  # Orange
            else:
                ovr_item.setForeground(QColor('#C62828'))  # Red
            
            self.players_table.setItem(row_idx, 2, ovr_item)
        
        # Update player count
        self.player_count_label.setText(f"Players: {len(players)}")
        
        # Re-enable sorting
        self.players_table.setSortingEnabled(True)
    
    def player_selected(self):
        """Handle player selection in the table"""
        selected_items = self.players_table.selectedItems()
        if selected_items:
            # Get player_id from first column
            player_id = selected_items[0].data(Qt.UserRole)
            self.selected_player_id = player_id
            self.load_player_details(player_id)
    
    def load_player_details(self, player_id):
        """Load and display detailed player information"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.first_name,
                    p.last_name,
                    p.height_inches,
                    p.weight,
                    p.age,
                    p.years_experience,
                    p.speed_40_time,
                    p.overall_rating,
                    p.skill_run,
                    p.skill_pass,
                    p.skill_receive,
                    p.skill_block,
                    p.skill_kick,
                    p.player_status,
                    pos.position_code,
                    pos.position_name,
                    r.jersey_number,
                    COALESCE(t.full_name, 'Free Agent') as team_name
                FROM players p
                JOIN positions pos ON p.position_id = pos.position_id
                LEFT JOIN roster r ON p.player_id = r.player_id AND r.is_active = TRUE
                LEFT JOIN teams t ON r.team_id = t.team_id
                WHERE p.player_id = ?
            """, (player_id,))
            
            player = cursor.fetchone()
            
            if player:
                # Show details widget, hide empty state
                self.empty_state_label.setVisible(False)
                self.details_widget.setVisible(True)
                
                # Update labels
                full_name = f"{player['first_name']} {player['last_name']}"
                self.player_name_label.setText(full_name)
                
                position_text = f"{player['position_code']} - {player['position_name']}"
                self.player_position_label.setText(position_text)
                
                # Physical attributes
                height_ft = player['height_inches'] // 12
                height_in = player['height_inches'] % 12
                self.height_label.setText(f"{height_ft}'{height_in}\"")
                self.weight_label.setText(f"{player['weight']} lbs")
                self.age_label.setText(str(player['age']) if player['age'] else 'N/A')
                
                if player['speed_40_time']:
                    self.speed_label.setText(f"{player['speed_40_time']:.2f}s")
                else:
                    self.speed_label.setText('N/A')
                
                # Skills with color coding
                self.overall_label.setText(
                    self.format_rating(player['overall_rating'])
                )
                self.run_label.setText(
                    self.format_rating(player['skill_run'])
                )
                self.pass_label.setText(
                    self.format_rating(player['skill_pass'])
                )
                self.receive_label.setText(
                    self.format_rating(player['skill_receive'])
                )
                self.block_label.setText(
                    self.format_rating(player['skill_block'])
                )
                self.kick_label.setText(
                    self.format_rating(player['skill_kick'])
                )
                
                # Career info
                self.team_label.setText(player['team_name'])
                
                if player['jersey_number']:
                    self.jersey_label.setText(f"#{player['jersey_number']}")
                else:
                    self.jersey_label.setText('N/A')
                
                years_exp = player['years_experience']
                if years_exp == 0:
                    self.experience_label.setText('Rookie')
                elif years_exp == 1:
                    self.experience_label.setText('1 year')
                else:
                    self.experience_label.setText(f"{years_exp} years")
                
                self.status_label.setText(player['player_status'])
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Error loading player details: {str(e)}")
    
    def format_rating(self, rating):
        """Format a rating with color HTML"""
        if rating >= 90:
            color = '#2E7D32'  # Dark green
        elif rating >= 80:
            color = '#1976D2'  # Blue
        elif rating >= 70:
            color = '#F57C00'  # Orange
        else:
            color = '#C62828'  # Red
        
        return f'<span style="color: {color}; font-weight: bold;">{rating}</span>'
