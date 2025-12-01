# Version: 2.0
# File: tabs/standings/standings_tab.py

"""
Standings Tab Module

Displays league standings with:
1. Full division standings (all teams ranked by division with tie-breakers)
2. Playoff picture (division leaders + wildcard contenders per conference)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QSplitter,
                            QGroupBox, QHeaderView, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

try:
    from utils.standings_calculator import calculate_division_leaders
except ImportError:
    print("Warning: standings_calculator not found")
    calculate_division_leaders = None


class StandingsTab(QWidget):
    """Standings display tab with division standings and playoff picture"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_league_id = None
        self.current_season = 1
        self.current_week = 1
        self.init_ui()
        self.load_initial_data()
        
    def load_initial_data(self):
        """Load initial league data and standings"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get active league and current season/week
            cursor.execute("""
                SELECT league_id, current_season, current_week 
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                self.current_league_id = result['league_id']
                self.current_season = result['current_season']
                self.current_week = result['current_week']
                self.load_league_info()
                self.refresh_standings()
                
        except Exception as e:
            print(f"Error loading initial data: {e}")
        
    def init_ui(self):
        """Initialize standings tab UI with split layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # Compact header with title and conference selector on same line
        header_layout = QHBoxLayout()
        
        title = QLabel("League Standings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addSpacing(20)
        header_layout.addWidget(QLabel("Conference:"))
        self.conference_combo = QComboBox()
        self.conference_combo.addItem("All Conferences", "ALL")
        self.conference_combo.currentIndexChanged.connect(self.refresh_standings)
        header_layout.addWidget(self.conference_combo)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Splitter for two main views
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Division standings
        self.division_widget = self.create_division_standings_widget()
        splitter.addWidget(self.division_widget)
        
        # Right side: Playoff picture
        self.playoff_widget = self.create_playoff_picture_widget()
        splitter.addWidget(self.playoff_widget)
        
        # Set initial splitter sizes (60% division, 40% playoff)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
    def create_division_standings_widget(self):
        """Create the division standings widget (left side)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Title
        title = QLabel("Division Standings")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(title)
        
        # Table
        self.division_table = QTableWidget()
        self.division_table.setColumnCount(7)
        self.division_table.setHorizontalHeaderLabels([
            "Division", "Team", "W-L-T", "Pct", "Div", "Conf", "Diff"
        ])
        
        # Set column widths
        header = self.division_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)            # Division
        header.resizeSection(0, 120)  # Wider for division names
        header.setSectionResizeMode(1, QHeaderView.Fixed)            # Team
        header.resizeSection(1, 200)  # Fixed reasonable width for team names
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # W-L-T
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Pct
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Div
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Conf
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Diff
        
        self.division_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.division_table)
        
        return widget
    
    def create_playoff_picture_widget(self):
        """Create the playoff picture widget (right side)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Title
        title = QLabel("Playoff Picture")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(title)
        
        # Info label
        self.playoff_info_label = QLabel("")
        self.playoff_info_label.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 5px;")
        layout.addWidget(self.playoff_info_label)
        
        # Table
        self.playoff_table = QTableWidget()
        self.playoff_table.setColumnCount(5)
        self.playoff_table.setHorizontalHeaderLabels([
            "Seed", "Team", "W-L-T", "Pct", "Status"
        ])
        
        # Set column widths
        header = self.playoff_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Seed
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Team
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # W-L-T
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Pct
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Status
        
        self.playoff_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.playoff_table)
        
        return widget
    
    def update_week(self, season, week):
        """Update standings for a specific week"""
        self.current_season = season
        self.current_week = week
        self.load_league_info()
        self.refresh_standings()
    
    def load_league_info(self):
        """Load league information and populate conference selector"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get active league
            cursor.execute("SELECT league_id FROM leagues WHERE is_active = TRUE LIMIT 1")
            league_result = cursor.fetchone()
            if league_result:
                self.current_league_id = league_result['league_id']
                
                # Load conferences for selector
                cursor.execute("""
                    SELECT conference_id, conference_name, abbreviation
                    FROM conferences
                    WHERE league_id = ?
                    ORDER BY conference_name
                """, (self.current_league_id,))
                
                conferences = cursor.fetchall()
                
                # Clear and repopulate conference combo (keep "All" option)
                while self.conference_combo.count() > 1:
                    self.conference_combo.removeItem(1)
                
                for conf in conferences:
                    self.conference_combo.addItem(
                        conf['conference_name'], 
                        conf['conference_id']
                    )
                    
        except Exception as e:
            print(f"Error loading league info: {e}")
    
    def refresh_standings(self):
        """Refresh both division standings and playoff picture"""
        self.load_division_standings()
        self.load_playoff_picture()
    
    def load_division_standings(self):
        """Load and display division standings with all teams ranked"""
        try:
            if not self.current_league_id or not calculate_division_leaders:
                self.show_no_data(self.division_table, "No standings data available")
                return
            
            # Get all teams with standings
            standings = calculate_division_leaders(
                self.current_league_id, 
                self.current_season, 
                self.db_manager
            )
            
            if not standings:
                self.show_no_data(self.division_table, "No standings data available")
                return
            
            # Filter by conference if selected
            selected_conf = self.conference_combo.currentData()
            if selected_conf != "ALL":
                standings = [t for t in standings if t['conference_id'] == selected_conf]
            
            # Group by division and maintain rank order
            divisions = {}
            division_order = []
            for team in standings:
                div_name = team['division_name']
                if div_name not in divisions:
                    divisions[div_name] = []
                    division_order.append(div_name)
                divisions[div_name].append(team)
            
            # Calculate total rows needed
            total_rows = len(standings)
            self.division_table.setRowCount(total_rows)
            
            # Populate table
            row = 0
            for div_name in division_order:
                div_teams = divisions[div_name]
                
                for idx, team in enumerate(div_teams):
                    # Division name (only show for first team in division)
                    if idx == 0:
                        div_item = QTableWidgetItem(div_name)
                        div_item.setFont(QFont("Arial", 12, QFont.Bold))
                        self.division_table.setItem(row, 0, div_item)
                    else:
                        self.division_table.setItem(row, 0, QTableWidgetItem(""))
                    
                    # Team name (highlight division leader with color, not different font)
                    team_text = f"{team['team_name']} ({team['abbreviation']})"
                    team_item = QTableWidgetItem(team_text)
                    if idx == 0:  # Division leader
                        team_item.setForeground(QColor("#006400"))  # Dark green
                    self.division_table.setItem(row, 1, team_item)
                    
                    # Overall record
                    record_text = f"{team['wins']}-{team['losses']}"
                    if team['ties'] > 0:
                        record_text += f"-{team['ties']}"
                    record_item = QTableWidgetItem(record_text)
                    record_item.setTextAlignment(Qt.AlignCenter)
                    self.division_table.setItem(row, 2, record_item)
                    
                    # Win percentage
                    pct_text = f"{team['win_pct']:.3f}"
                    pct_item = QTableWidgetItem(pct_text)
                    pct_item.setTextAlignment(Qt.AlignCenter)
                    self.division_table.setItem(row, 3, pct_item)
                    
                    # Division record
                    div_record_text = f"{team['div_wins']}-{team['div_losses']}"
                    div_record_item = QTableWidgetItem(div_record_text)
                    div_record_item.setTextAlignment(Qt.AlignCenter)
                    self.division_table.setItem(row, 4, div_record_item)
                    
                    # Conference record
                    conf_record_text = f"{team['conf_wins']}-{team['conf_losses']}"
                    conf_record_item = QTableWidgetItem(conf_record_text)
                    conf_record_item.setTextAlignment(Qt.AlignCenter)
                    self.division_table.setItem(row, 5, conf_record_item)
                    
                    # Point differential
                    diff_text = f"{team['points_diff']:+d}" if team['points_diff'] != 0 else "0"
                    diff_item = QTableWidgetItem(diff_text)
                    diff_item.setTextAlignment(Qt.AlignCenter)
                    self.division_table.setItem(row, 6, diff_item)
                    
                    row += 1
            
        except Exception as e:
            self.show_no_data(self.division_table, f"Error loading standings: {str(e)}")
            print(f"Error loading division standings: {e}")
    
    def load_playoff_picture(self):
        """Load and display playoff picture with division leaders and wildcard contenders"""
        try:
            if not self.current_league_id or not calculate_division_leaders:
                self.show_no_data(self.playoff_table, "No playoff data available")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get playoff configuration
            cursor.execute("""
                SELECT playoff_teams_per_conf 
                FROM leagues 
                WHERE league_id = ?
            """, (self.current_league_id,))
            
            result = cursor.fetchone()
            if not result:
                self.show_no_data(self.playoff_table, "League configuration not found")
                return
            
            playoff_teams_per_conf = result['playoff_teams_per_conf'] or 7
            
            # Get all teams with standings
            standings = calculate_division_leaders(
                self.current_league_id, 
                self.current_season, 
                self.db_manager
            )
            
            if not standings:
                self.show_no_data(self.playoff_table, "No playoff data available")
                return
            
            # Filter by conference if selected
            selected_conf = self.conference_combo.currentData()
            if selected_conf != "ALL":
                standings = [t for t in standings if t['conference_id'] == selected_conf]
                conferences_to_show = [selected_conf]
            else:
                # Get all conferences
                cursor.execute("""
                    SELECT DISTINCT conference_id 
                    FROM teams 
                    WHERE league_id = ?
                    ORDER BY conference_id
                """, (self.current_league_id,))
                conferences_to_show = [row['conference_id'] for row in cursor.fetchall()]
            
            # Update info label
            wildcard_count = playoff_teams_per_conf - 4  # Assuming 4 divisions per conference
            self.playoff_info_label.setText(
                f"Top {playoff_teams_per_conf} teams per conference "
                f"(4 division leaders + {wildcard_count} wildcards)"
            )
            
            # Calculate playoff teams for each conference
            all_playoff_teams = []
            
            for conf_id in conferences_to_show:
                # Get teams in this conference
                conf_teams = [t for t in standings if t['conference_id'] == conf_id]
                
                # Identify division leaders (first place team from each division)
                division_leaders = {}
                divisions_seen = set()
                for team in conf_teams:
                    div_id = team['division_id']
                    if div_id not in divisions_seen:
                        division_leaders[div_id] = team
                        divisions_seen.add(div_id)
                        team['is_division_leader'] = True
                
                # Get remaining teams (non-division leaders) for wildcard
                wildcard_contenders = [
                    t for t in conf_teams 
                    if t['team_id'] not in [dl['team_id'] for dl in division_leaders.values()]
                ]
                
                # Sort division leaders by record to assign seeds 1-4
                from utils.standings_calculator import sort_teams_with_tiebreakers
                #sorted_division_leaders = sort_teams_with_tiebreakers(list(division_leaders.values()))
                sorted_division_leaders = sort_teams_with_tiebreakers(list(division_leaders.values()), 
                                                                      cursor, self.current_season, 
                                                                      self.current_league_id)
                
                # Sort wildcard contenders by record with proper head-to-head
                sorted_wildcards = self.sort_wildcard_teams(
                    wildcard_contenders, 
                    self.current_league_id, 
                    self.current_season
                )
                
                # Assign seeds: division leaders get seeds 1-4, then wildcards get remaining seeds
                playoff_roster = []
                
                # Seeds 1-4: Division leaders
                for idx, team in enumerate(sorted_division_leaders):
                    team['playoff_seed'] = idx + 1
                    team['playoff_status'] = f"Division Leader (#{team['playoff_seed']} seed)"
                    playoff_roster.append(team)
                
                # Seeds 5+: Wildcard teams
                num_wildcards = playoff_teams_per_conf - len(sorted_division_leaders)
                for idx, team in enumerate(sorted_wildcards[:num_wildcards]):
                    team['playoff_seed'] = len(sorted_division_leaders) + idx + 1
                    team['is_division_leader'] = False
                    wildcard_num = idx + 1
                    team['playoff_status'] = f"Wildcard #{wildcard_num} (#{team['playoff_seed']} seed)"
                    playoff_roster.append(team)
                
                # Add teams just outside playoff picture for context (in the hunt)
                for idx, team in enumerate(sorted_wildcards[num_wildcards:num_wildcards + 3]):
                    team['playoff_seed'] = None
                    team['is_division_leader'] = False
                    team['playoff_status'] = "In the Hunt"
                    playoff_roster.append(team)
                
                # Add to overall list
                all_playoff_teams.extend(playoff_roster)
            
            # Populate table
            self.playoff_table.setRowCount(len(all_playoff_teams))
            
            for row, team in enumerate(all_playoff_teams):
                # Seed
                if team.get('playoff_seed'):
                    seed_text = str(team['playoff_seed'])
                    seed_item = QTableWidgetItem(seed_text)
                    seed_item.setTextAlignment(Qt.AlignCenter)
                    seed_item.setFont(QFont("Arial", 9, QFont.Bold))
                else:
                    seed_text = "-"
                    seed_item = QTableWidgetItem(seed_text)
                    seed_item.setTextAlignment(Qt.AlignCenter)
                self.playoff_table.setItem(row, 0, seed_item)
                
                # Team name
                team_text = f"{team['team_name']} ({team['abbreviation']})"
                team_item = QTableWidgetItem(team_text)
                if team.get('playoff_seed'):
                    if team.get('is_division_leader'):
                        team_item.setForeground(QColor("#006400"))  # Dark green for division leaders
                    else:
                        team_item.setForeground(QColor("#0066CC"))  # Blue for wildcards
                else:
                    team_item.setForeground(QColor("#888888"))  # Gray for "in the hunt"
                self.playoff_table.setItem(row, 1, team_item)
                
                # Overall record
                record_text = f"{team['wins']}-{team['losses']}"
                if team['ties'] > 0:
                    record_text += f"-{team['ties']}"
                record_item = QTableWidgetItem(record_text)
                record_item.setTextAlignment(Qt.AlignCenter)
                self.playoff_table.setItem(row, 2, record_item)
                
                # Win percentage
                pct_text = f"{team['win_pct']:.3f}"
                pct_item = QTableWidgetItem(pct_text)
                pct_item.setTextAlignment(Qt.AlignCenter)
                self.playoff_table.setItem(row, 3, pct_item)
                
                # Playoff status
                status_item = QTableWidgetItem(team['playoff_status'])
                if team.get('playoff_seed'):
                    status_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.playoff_table.setItem(row, 4, status_item)
            
        except Exception as e:
            self.show_no_data(self.playoff_table, f"Error loading playoff picture: {str(e)}")
            print(f"Error loading playoff picture: {e}")
    
    def sort_wildcard_teams(self, teams, league_id, season):
        """
        Sort wildcard teams with proper head-to-head tie-breakers.
        For teams with the same record, check if they've played each other.
        """
        if not teams:
            return []
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Group teams by win percentage
        from collections import defaultdict
        by_record = defaultdict(list)
        for team in teams:
            by_record[team['win_pct']].append(team)
        
        # Sort each group by tie-breakers
        sorted_teams = []
        for win_pct in sorted(by_record.keys(), reverse=True):
            tied_teams = by_record[win_pct]
            
            if len(tied_teams) == 1:
                sorted_teams.extend(tied_teams)
            else:
                # Teams are tied - apply head-to-head if they've played
                sorted_group = self.break_ties_with_h2h(tied_teams, cursor, season, league_id)
                sorted_teams.extend(sorted_group)
        
        return sorted_teams
    
    def break_ties_with_h2h(self, tied_teams, cursor, season, league_id):
        """Break ties using head-to-head records between the tied teams"""
        if len(tied_teams) <= 1:
            return tied_teams
        
        # Calculate head-to-head record among these specific teams
        team_ids = [t['team_id'] for t in tied_teams]
        h2h_records = {}
        
        for team in tied_teams:
            team_id = team['team_id']
            
            # Get wins/losses against other teams in this tied group
            query = """
                SELECT 
                    SUM(CASE 
                        WHEN (g.home_team_id = ? AND g.home_score > g.away_score) 
                          OR (g.away_team_id = ? AND g.away_score > g.home_score) 
                        THEN 1 ELSE 0 END) as wins,
                    SUM(CASE 
                        WHEN (g.home_team_id = ? AND g.home_score < g.away_score) 
                          OR (g.away_team_id = ? AND g.away_score < g.home_score) 
                        THEN 1 ELSE 0 END) as losses
                FROM games g
                WHERE (g.home_team_id = ? OR g.away_team_id = ?)
                    AND (
                        (g.home_team_id IN ({}) AND g.away_team_id = ?)
                        OR (g.away_team_id IN ({}) AND g.home_team_id = ?)
                    )
                    AND g.game_status = 'COMPLETED'
                    AND g.season = ?
                    AND g.league_id = ?
            """.format(','.join('?' * len(team_ids)), ','.join('?' * len(team_ids)))
            
            params = [team_id, team_id, team_id, team_id, team_id, team_id] + \
                     team_ids + [team_id] + team_ids + [team_id, season, league_id]
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            h2h_wins = result['wins'] or 0
            h2h_losses = result['losses'] or 0
            h2h_records[team_id] = (h2h_wins, h2h_losses)
        
        # Sort by head-to-head percentage, then other tie-breakers
        def sort_key(team):
            h2h_wins, h2h_losses = h2h_records[team['team_id']]
            h2h_pct = h2h_wins / (h2h_wins + h2h_losses) if (h2h_wins + h2h_losses) > 0 else 0
            
            conf_pct = (team['conf_wins'] / (team['conf_wins'] + team['conf_losses']) 
                       if (team['conf_wins'] + team['conf_losses']) > 0 else 0)
            
            return (
                -h2h_pct,                # Head-to-head among tied teams
                -conf_pct,               # Conference record
                -team['points_diff'],    # Points differential
                -team['points_for']      # Points scored
            )
        
        return sorted(tied_teams, key=sort_key)
    
    def show_no_data(self, table, message):
        """Show a message when no data is available"""
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(0, 0, item)
