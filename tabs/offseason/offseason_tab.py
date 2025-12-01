# ========================================
# tabs/offseason/offseason_tab.py
# Version: 2.1
# Path: tabs/offseason/offseason_tab.py
# ========================================

"""
Offseason Management Tab Module

Season transition workflow including player aging, skill updates,
retirements, rookie generation, draft preparation, and season advancement.

Features:
- Phase 1: Season Finalization (Archive Season, Calculate Awards)
- Phase 2: Player Management (Age, Skills, Retirements)
- Phase 3: Draft Preparation (Rookie Class, Draft Order)
- Phase 4: Season Start (Conduct Draft, Generate Schedule)

Version 2.1 - Now populates offseason_tasks table when archiving
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt
from datetime import datetime
import json

# Import offseason utilities
try:
    from utils.age_players import age_players
except ImportError:
    print("[OFFSEASON] Warning: age_players utility not found")
    age_players = None

try:
    from utils.update_skills import update_player_skills
except ImportError:
    print("[OFFSEASON] Warning: update_skills utility not found")
    update_player_skills = None


class OffseasonTab(QWidget):
    """Offseason management tab - season transition workflow"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_league_id = None
        self.current_season = 1
        self.season_archived = False
        self.init_ui()
        self.load_season_status()
        
    def init_ui(self):
        """Initialize offseason tab UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Title
        title = QLabel("Offseason Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Season Status Card (compact)
        self.status_card = self.create_status_card()
        main_layout.addWidget(self.status_card)
        
        # Phase 1: Season Finalization
        phase1 = self.create_phase1_group()
        main_layout.addWidget(phase1)
        
        # Phase 2: Player Management
        phase2 = self.create_phase2_group()
        main_layout.addWidget(phase2)
        
        # Phase 3: Draft Preparation
        phase3 = self.create_phase3_group()
        main_layout.addWidget(phase3)
        
        # Phase 4: Season Start
        phase4 = self.create_phase4_group()
        main_layout.addWidget(phase4)
        
        main_layout.addStretch()
    
    def create_status_card(self):
        """Create compact season status display card"""
        card = QGroupBox("Current Season Status")
        card.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 6px;
                padding: 8px;
                background-color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(15)
        
        # Season info
        self.season_label = QLabel("Season: Loading...")
        self.season_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.season_label)
        
        # Separator
        sep1 = QLabel("|")
        sep1.setStyleSheet("color: #95a5a6;")
        layout.addWidget(sep1)
        
        # Status info
        self.status_label = QLabel("Status: Loading...")
        self.status_label.setStyleSheet("font-size: 12px; color: #34495e;")
        layout.addWidget(self.status_label)
        
        # Separator
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #95a5a6;")
        layout.addWidget(sep2)
        
        # Championship info
        self.champion_label = QLabel("")
        self.champion_label.setStyleSheet("font-size: 12px; color: #27ae60;")
        layout.addWidget(self.champion_label)
        
        layout.addStretch()
        
        return card
    
    def create_phase1_group(self):
        """Create Phase 1: Season Finalization group"""
        group = QGroupBox("Phase 1: Season Finalization")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 5px;
                margin-top: 6px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #27ae60;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        
        # Archive Season Button Row
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        self.archive_btn = QPushButton("🏆 Archive Season")
        self.archive_btn.setFixedWidth(200)
        self.archive_btn.setToolTip("Save championship results and prepare for next season")
        self.archive_btn.clicked.connect(self.archive_season)
        self.archive_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """)
        row1.addWidget(self.archive_btn)
        
        desc1 = QLabel("Create permanent record of season champion and statistics")
        desc1.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc1.setWordWrap(True)
        row1.addWidget(desc1, 1)
        
        layout.addLayout(row1)
        
        # Calculate Awards Button Row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        awards_btn = QPushButton("🏅 Calculate Awards")
        awards_btn.setFixedWidth(200)
        awards_btn.setToolTip("To be implemented - Calculate season awards")
        awards_btn.clicked.connect(lambda: self.show_stub_message("Calculate Season Awards"))
        awards_btn.setStyleSheet(self.get_stub_button_style())
        row2.addWidget(awards_btn)
        
        desc2 = QLabel("Determine MVP, Offensive/Defensive Player of Year, and other awards")
        desc2.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc2.setWordWrap(True)
        row2.addWidget(desc2, 1)
        
        layout.addLayout(row2)
        
        return group
    
    def create_phase2_group(self):
        """Create Phase 2: Player Management group"""
        group = QGroupBox("Phase 2: Player Management")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 5px;
                margin-top: 6px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #d35400;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        
        # Age Players Button Row
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        age_btn = QPushButton("🎂 Age Players")
        age_btn.setFixedWidth(200)
        age_btn.setToolTip("Add one year to all player ages")
        age_btn.clicked.connect(self.age_players)
        age_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        row1.addWidget(age_btn)
        
        desc1 = QLabel("Add one year to age of all players in the league")
        desc1.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc1.setWordWrap(True)
        row1.addWidget(desc1, 1)
        
        layout.addLayout(row1)
        
        # Update Skills Button Row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        skills_btn = QPushButton("📈 Update Skills")
        skills_btn.setFixedWidth(200)
        skills_btn.setToolTip("Apply skill progression/regression based on age")
        skills_btn.clicked.connect(self.update_player_skills)
        skills_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        row2.addWidget(skills_btn)
        
        desc2 = QLabel("Apply skill changes based on age and performance")
        desc2.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc2.setWordWrap(True)
        row2.addWidget(desc2, 1)
        
        layout.addLayout(row2)
        
        # Process Retirements Button Row
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        
        retire_btn = QPushButton("👴 Retirements")
        retire_btn.setFixedWidth(200)
        retire_btn.setToolTip("To be implemented - Remove retiring players")
        retire_btn.clicked.connect(lambda: self.show_stub_message("Process Retirements"))
        retire_btn.setStyleSheet(self.get_stub_button_style())
        row3.addWidget(retire_btn)
        
        desc3 = QLabel("Automatically retire players based on age and performance")
        desc3.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc3.setWordWrap(True)
        row3.addWidget(desc3, 1)
        
        layout.addLayout(row3)
        
        return group
    
    def create_phase3_group(self):
        """Create Phase 3: Draft Preparation group"""
        group = QGroupBox("Phase 3: Draft Preparation")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 6px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #8e44ad;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        
        # Generate Rookies Button Row
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        rookies_btn = QPushButton("👶 Generate Rookies")
        rookies_btn.setFixedWidth(200)
        rookies_btn.setToolTip("To be implemented - Create draft prospects")
        rookies_btn.clicked.connect(lambda: self.show_stub_message("Generate Rookie Class"))
        rookies_btn.setStyleSheet(self.get_stub_button_style())
        row1.addWidget(rookies_btn)
        
        desc1 = QLabel("Create new draft prospects with randomized ratings and attributes")
        desc1.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc1.setWordWrap(True)
        row1.addWidget(desc1, 1)
        
        layout.addLayout(row1)
        
        # Calculate Draft Order Button Row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        draft_order_btn = QPushButton("📋 Draft Order")
        draft_order_btn.setFixedWidth(200)
        draft_order_btn.setToolTip("To be implemented - Determine draft pick order")
        draft_order_btn.clicked.connect(lambda: self.show_stub_message("Calculate Draft Order"))
        draft_order_btn.setStyleSheet(self.get_stub_button_style())
        row2.addWidget(draft_order_btn)
        
        desc2 = QLabel("Set draft order based on previous season standings (worst to best)")
        desc2.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc2.setWordWrap(True)
        row2.addWidget(desc2, 1)
        
        layout.addLayout(row2)
        
        return group
    
    def create_phase4_group(self):
        """Create Phase 4: Season Start group"""
        group = QGroupBox("Phase 4: Season Start")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                margin-top: 6px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #c0392b;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(6)
        
        # Conduct Draft Button Row
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        draft_btn = QPushButton("🎯 Conduct Draft")
        draft_btn.setFixedWidth(200)
        draft_btn.setToolTip("To be implemented - Run draft simulation")
        draft_btn.clicked.connect(lambda: self.show_stub_message("Conduct Draft"))
        draft_btn.setStyleSheet(self.get_stub_button_style())
        row1.addWidget(draft_btn)
        
        desc1 = QLabel("Execute the draft - teams select players from rookie class")
        desc1.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc1.setWordWrap(True)
        row1.addWidget(desc1, 1)
        
        layout.addLayout(row1)
        
        # Generate Schedule Button Row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        schedule_btn = QPushButton("📅 New Schedule")
        schedule_btn.setFixedWidth(200)
        schedule_btn.setToolTip("To be implemented - Create schedule for new season")
        schedule_btn.clicked.connect(lambda: self.show_stub_message("Generate Schedule"))
        schedule_btn.setStyleSheet(self.get_stub_button_style())
        row2.addWidget(schedule_btn)
        
        desc2 = QLabel("Create game schedule for the upcoming season")
        desc2.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc2.setWordWrap(True)
        row2.addWidget(desc2, 1)
        
        layout.addLayout(row2)
        
        return group
    
    def get_stub_button_style(self):
        """Get standard style for stub buttons"""
        return """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a89;
            }
        """
    
    def load_season_status(self):
        """Load current season status and update UI"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get current league and season
            cursor.execute("""
                SELECT league_id, league_name, current_season, current_week
                FROM leagues 
                WHERE is_active = TRUE 
                LIMIT 1
            """)
            
            league = cursor.fetchone()
            if not league:
                self.season_label.setText("Season: No active league found")
                self.status_label.setText("Status: Please create a league first")
                self.archive_btn.setEnabled(False)
                return
            
            self.current_league_id = league['league_id']
            self.current_season = league['current_season']
            
            self.season_label.setText(f"Season: {self.current_season}")
            
            # Check if season already archived
            cursor.execute("""
                SELECT season_id, superbowl_winner_team_id, superbowl_loser_team_id,
                       superbowl_score_winner, superbowl_score_loser
                FROM seasons 
                WHERE league_id = ? AND season_number = ?
            """, (self.current_league_id, self.current_season))
            
            archived = cursor.fetchone()
            
            if archived and archived['superbowl_winner_team_id']:
                self.season_archived = True
                self.status_label.setText("Status: ✅ Season Archived")
                self.status_label.setStyleSheet("font-size: 14px; color: #27ae60; margin-top: 5px; font-weight: bold;")
                
                # Get champion name
                cursor.execute("""
                    SELECT full_name, abbreviation 
                    FROM teams 
                    WHERE team_id = ?
                """, (archived['superbowl_winner_team_id'],))
                winner = cursor.fetchone()
                
                cursor.execute("""
                    SELECT full_name, abbreviation 
                    FROM teams 
                    WHERE team_id = ?
                """, (archived['superbowl_loser_team_id'],))
                loser = cursor.fetchone()
                
                if winner and loser:
                    self.champion_label.setText(
                        f"🏆 {winner['abbreviation']} {archived['superbowl_score_winner']}-{archived['superbowl_score_loser']} {loser['abbreviation']}"
                    )
                    self.archive_btn.setText("🔄 Re-Archive Season")
            else:
                # Check if Super Bowl has been played
                cursor.execute("""
                    SELECT game_id, home_team_id, away_team_id, home_score, away_score, game_status
                    FROM games
                    WHERE league_id = ? AND season = ? AND game_type = 'SUPERBOWL'
                """, (self.current_league_id, self.current_season))
                
                superbowl = cursor.fetchone()
                
                if superbowl and superbowl['game_status'] == 'COMPLETED':
                    self.season_archived = False
                    self.status_label.setText("Status: ✅ Super Bowl Complete - Ready to Archive")
                    self.status_label.setStyleSheet("font-size: 14px; color: #f39c12; margin-top: 5px; font-weight: bold;")
                    self.archive_btn.setEnabled(True)
                    
                    # Show who won
                    winner_id = superbowl['home_team_id'] if superbowl['home_score'] > superbowl['away_score'] else superbowl['away_team_id']
                    cursor.execute("SELECT abbreviation FROM teams WHERE team_id = ?", (winner_id,))
                    winner = cursor.fetchone()
                    if winner:
                        self.champion_label.setText(f"🏆 SB Winner: {winner['abbreviation']}")
                else:
                    self.season_archived = False
                    self.status_label.setText("Status: Season In Progress")
                    self.status_label.setStyleSheet("font-size: 14px; color: #e74c3c; margin-top: 5px;")
                    self.champion_label.setText("⚠️ Complete Super Bowl before archiving season")
                    self.archive_btn.setEnabled(False)
                    self.archive_btn.setToolTip("Complete the Super Bowl first")
            
        except Exception as e:
            print(f"Error loading season status: {e}")
            self.status_label.setText(f"Status: Error loading data - {str(e)}")
            import traceback
            traceback.print_exc()
    
    def initialize_offseason_tasks(self, cursor, from_season, to_season):
        """Initialize all 9 offseason tasks for season transition"""
        try:
            # First, check if the offseason_tasks table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='offseason_tasks'
            """)
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print(f"[OFFSEASON] ⚠️ WARNING: offseason_tasks table does not exist!")
                print(f"[OFFSEASON] Please run offseason_tasks.ddl to create the table")
                return
            
            print(f"[OFFSEASON] ✓ offseason_tasks table exists")
            
            # Define all offseason tasks
            tasks = [
                ('Archive Season', 1, False),
                ('Calculate Season Awards', 2, True),
                ('Age Players', 3, False),
                ('Update Player Skills', 4, True),
                ('Process Retirements', 5, False),
                ('Generate Rookie Class', 6, True),
                ('Calculate Draft Order', 7, True),
                ('Conduct Draft', 8, False),
                ('Generate New Season Schedule', 9, False)
            ]
            
            # Check if tasks already exist for this season
            cursor.execute("""
                SELECT COUNT(*) as count FROM offseason_tasks
                WHERE league_id = ? AND from_season = ?
            """, (self.current_league_id, from_season))
            
            result = cursor.fetchone()
            # Handle both dictionary and tuple access
            existing_count = result['count'] if isinstance(result, dict) or hasattr(result, 'keys') else result[0]
            
            if existing_count > 0:
                print(f"[OFFSEASON] Tasks already exist for season {from_season} (found {existing_count} tasks)")
                return
            
            print(f"[OFFSEASON] No existing tasks found, creating {len(tasks)} tasks...")
            
            # Insert all tasks
            for task_name, task_order, is_reversible in tasks:
                cursor.execute("""
                    INSERT INTO offseason_tasks (
                        league_id, from_season, to_season,
                        task_name, task_order, is_complete, is_reversible
                    ) VALUES (?, ?, ?, ?, ?, 0, ?)
                """, (self.current_league_id, from_season, to_season, 
                      task_name, task_order, is_reversible))
                print(f"[OFFSEASON]   ✓ Created task: {task_name}")
            
            print(f"[OFFSEASON] ✅ Successfully initialized {len(tasks)} offseason tasks")
            
        except Exception as e:
            print(f"[OFFSEASON] ❌ ERROR in initialize_offseason_tasks: {e}")
            import traceback
            traceback.print_exc()
    
    def mark_task_complete(self, cursor, task_name, metadata=None):
        """Mark a task as complete with optional metadata"""
        try:
            # First check if the task exists
            cursor.execute("""
                SELECT task_id FROM offseason_tasks
                WHERE league_id = ? AND from_season = ? AND task_name = ?
            """, (self.current_league_id, self.current_season, task_name))
            
            existing_task = cursor.fetchone()
            
            if not existing_task:
                print(f"[OFFSEASON] ⚠️ WARNING: Task '{task_name}' not found in offseason_tasks table")
                print(f"[OFFSEASON]   League ID: {self.current_league_id}, Season: {self.current_season}")
                return
            
            # Update the task
            cursor.execute("""
                UPDATE offseason_tasks
                SET is_complete = 1,
                    completed_date = ?,
                    completed_by = 'USER',
                    task_metadata = ?
                WHERE league_id = ? AND from_season = ? AND task_name = ?
            """, (
                datetime.now().isoformat(),
                json.dumps(metadata) if metadata else None,
                self.current_league_id,
                self.current_season,
                task_name
            ))
            
            print(f"[OFFSEASON] ✓ Marked '{task_name}' as complete")
            
            if metadata:
                print(f"[OFFSEASON]   Metadata: {json.dumps(metadata, indent=2)}")
                
        except Exception as e:
            print(f"[OFFSEASON] ❌ ERROR in mark_task_complete: {e}")
            import traceback
            traceback.print_exc()
    
    def archive_season(self):
        """Archive the current season - create historical record"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if already archived
            cursor.execute("""
                SELECT season_id 
                FROM seasons 
                WHERE league_id = ? AND season_number = ?
            """, (self.current_league_id, self.current_season))
            
            existing = cursor.fetchone()
            
            if existing:
                # Ask if user wants to re-archive
                reply = QMessageBox.question(
                    self,
                    "Season Already Archived",
                    f"Season {self.current_season} has already been archived.\n\n"
                    "Do you want to clear the existing record and re-archive?\n"
                    "(This will update the championship information)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
                
                # Delete existing record
                cursor.execute("DELETE FROM seasons WHERE season_id = ?", (existing['season_id'],))
                print(f"[OFFSEASON] Deleted existing season record for Season {self.current_season}")
            
            # Find Super Bowl game
            cursor.execute("""
                SELECT game_id, home_team_id, away_team_id, home_score, away_score, game_status
                FROM games
                WHERE league_id = ? AND season = ? AND game_type = 'SUPERBOWL'
            """, (self.current_league_id, self.current_season))
            
            superbowl = cursor.fetchone()
            
            if not superbowl:
                QMessageBox.warning(
                    self,
                    "No Super Bowl Found",
                    f"No Super Bowl game found for Season {self.current_season}.\n\n"
                    "Generate playoff games first."
                )
                return
            
            if superbowl['game_status'] != 'COMPLETED':
                QMessageBox.warning(
                    self,
                    "Super Bowl Not Complete",
                    f"The Super Bowl has not been completed yet.\n\n"
                    "Play the Super Bowl game before archiving the season."
                )
                return
            
            # Determine winner and loser
            if superbowl['home_score'] > superbowl['away_score']:
                winner_id = superbowl['home_team_id']
                loser_id = superbowl['away_team_id']
                winner_score = superbowl['home_score']
                loser_score = superbowl['away_score']
            else:
                winner_id = superbowl['away_team_id']
                loser_id = superbowl['home_team_id']
                winner_score = superbowl['away_score']
                loser_score = superbowl['home_score']
            
            # Get team names for confirmation
            cursor.execute("SELECT full_name, abbreviation FROM teams WHERE team_id = ?", (winner_id,))
            winner = cursor.fetchone()
            cursor.execute("SELECT full_name, abbreviation FROM teams WHERE team_id = ?", (loser_id,))
            loser = cursor.fetchone()
            
            # Confirm with user
            reply = QMessageBox.question(
                self,
                "Archive Season?",
                f"Archive Season {self.current_season}?\n\n"
                f"🏆 Champion: {winner['full_name']} ({winner_score})\n"
                f"🥈 Runner-up: {loser['full_name']} ({loser_score})\n\n"
                f"This will create a permanent historical record.\n"
                f"Ready to advance to Season {self.current_season + 1}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                print(f"[OFFSEASON] User cancelled archiving")
                return
            
            # Count total games
            cursor.execute("""
                SELECT COUNT(*) as total_games
                FROM games
                WHERE league_id = ? AND season = ? AND game_status = 'COMPLETED'
            """, (self.current_league_id, self.current_season))
            total_games = cursor.fetchone()['total_games']
            
            # Find highest scoring game
            cursor.execute("""
                SELECT game_id, (home_score + away_score) as total_score
                FROM games
                WHERE league_id = ? AND season = ? AND game_status = 'COMPLETED'
                ORDER BY total_score DESC
                LIMIT 1
            """, (self.current_league_id, self.current_season))
            highest_scoring = cursor.fetchone()
            highest_scoring_game_id = highest_scoring['game_id'] if highest_scoring else None
            
            # Find team with most wins
            cursor.execute("""
                SELECT team_id, COUNT(*) as wins
                FROM (
                    SELECT home_team_id as team_id
                    FROM games
                    WHERE league_id = ? AND season = ? 
                      AND game_status = 'COMPLETED'
                      AND game_type = 'REGULAR'
                      AND home_score > away_score
                    UNION ALL
                    SELECT away_team_id as team_id
                    FROM games
                    WHERE league_id = ? AND season = ?
                      AND game_status = 'COMPLETED'
                      AND game_type = 'REGULAR'
                      AND away_score > home_score
                )
                GROUP BY team_id
                ORDER BY wins DESC
                LIMIT 1
            """, (self.current_league_id, self.current_season, 
                  self.current_league_id, self.current_season))
            most_wins = cursor.fetchone()
            most_wins_team_id = most_wins['team_id'] if most_wins else None
            most_wins_count = most_wins['wins'] if most_wins else 0
            
            # Insert season record
            cursor.execute("""
                INSERT INTO seasons (
                    league_id, season_number, season_status,
                    superbowl_winner_team_id, superbowl_loser_team_id,
                    superbowl_score_winner, superbowl_score_loser,
                    superbowl_game_id,
                    total_games_played,
                    highest_scoring_game_id,
                    most_wins_team_id,
                    most_wins_count,
                    season_end_date,
                    archived_date
                ) VALUES (?, ?, 'COMPLETE', ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), DATETIME('now'))
            """, (
                self.current_league_id, self.current_season,
                winner_id, loser_id, winner_score, loser_score,
                superbowl['game_id'],
                total_games,
                highest_scoring_game_id,
                most_wins_team_id,
                most_wins_count
            ))
            
            conn.commit()
            print(f"[OFFSEASON] ✅ Season record committed to database")
            
            # Initialize offseason tasks and mark Archive Season as complete
            print(f"[OFFSEASON] Starting offseason tasks initialization...")
            next_season = self.current_season + 1
            
            try:
                self.initialize_offseason_tasks(cursor, self.current_season, next_season)
                
                # Mark Archive Season task as complete with metadata
                archive_metadata = {
                    'champion_team_id': winner_id,
                    'champion_name': winner['full_name'],
                    'total_games': total_games,
                    'archived_date': datetime.now().isoformat()
                }
                
                self.mark_task_complete(cursor, 'Archive Season', archive_metadata)
                
                # Commit the offseason tasks changes
                conn.commit()
                print(f"[OFFSEASON] ✅ Offseason tasks committed to database")
                
            except Exception as task_error:
                print(f"[OFFSEASON] ⚠️ Error with offseason tasks (non-fatal): {task_error}")
                import traceback
                traceback.print_exc()
                # Don't fail the whole operation if tasks fail
            
            print(f"[OFFSEASON] ✅ Season {self.current_season} archived successfully!")
            print(f"[OFFSEASON]   Champion: {winner['full_name']} ({winner_score}-{loser_score})")
            print(f"[OFFSEASON]   Total Games: {total_games}")
            
            # Refresh UI
            self.load_season_status()
            
            # Success message
            QMessageBox.information(
                self,
                "Season Archived!",
                f"Season {self.current_season} has been archived!\n\n"
                f"🏆 Champion: {winner['full_name']}\n"
                f"📊 Games Played: {total_games}\n\n"
                f"✅ Offseason tasks initialized\n"
                f"✅ 'Archive Season' marked complete\n\n"
                f"Check console for detailed task information.\n\n"
                f"You can now proceed with offseason tasks.\n"
                f"When ready, generate schedule for Season {next_season}."
            )
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(
                self,
                "Archive Error",
                f"Error archiving season:\n\n{str(e)}"
            )
            print(f"[OFFSEASON] Error archiving season: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def age_players(self):
        """Age all players in the league by one year"""
        if not age_players:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                "Age Players utility not found.\n\n"
                "Make sure utils/age_players.py exists."
            )
            return
        
        # Check if task already complete
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT is_complete FROM offseason_tasks
                WHERE league_id = ? AND from_season = ? AND task_name = 'Age Players'
            """, (self.current_league_id, self.current_season))
            
            task = cursor.fetchone()
            if task:
                is_complete = task['is_complete'] if isinstance(task, dict) or hasattr(task, 'keys') else task[0]
                if is_complete:
                    reply = QMessageBox.question(
                        self,
                        "Task Already Complete",
                        "Players have already been aged for this season.\n\n"
                        "Do you want to age them again?\n"
                        "(This will add another year to all players)",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
        except Exception as e:
            print(f"[OFFSEASON] Warning checking task status: {e}")
        finally:
            if conn:
                conn.close()
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Age All Players?",
            f"Add one year to all players in Season {self.current_season}?\n\n"
            "This will:\n"
            "• Add 1 year to every player's age\n"
            "• Update league average age\n"
            "• Affect retirement eligibility\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            print(f"[OFFSEASON] User cancelled age players")
            return
        
        print(f"[OFFSEASON] Starting age players process...")
        
        # Call the utility function
        result = age_players(self.db_manager.db_path, self.current_league_id, self.current_season)
        
        if result['success']:
            # Mark task complete with a fresh connection
            conn = None
            cursor = None
            try:
                # Get a fresh connection
                import sqlite3
                conn = sqlite3.connect(self.db_manager.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                print(f"[OFFSEASON] Marking task complete...")
                
                # Prepare metadata
                metadata = {
                    'players_aged': result['players_aged'],
                    'avg_age_before': result['details']['before']['avg_age'],
                    'avg_age_after': result['details']['after']['avg_age'],
                    'players_35_plus': result['details']['after']['age_35_plus'],
                    'completed_date': datetime.now().isoformat()
                }
                
                # Check if task exists
                cursor.execute("""
                    SELECT task_id FROM offseason_tasks
                    WHERE league_id = ? AND from_season = ? AND task_name = 'Age Players'
                """, (self.current_league_id, self.current_season))
                
                existing_task = cursor.fetchone()
                
                if existing_task:
                    # Update the task
                    cursor.execute("""
                        UPDATE offseason_tasks
                        SET is_complete = 1,
                            completed_date = ?,
                            completed_by = 'USER',
                            task_metadata = ?
                        WHERE league_id = ? AND from_season = ? AND task_name = 'Age Players'
                    """, (
                        datetime.now().isoformat(),
                        json.dumps(metadata),
                        self.current_league_id,
                        self.current_season
                    ))
                    
                    conn.commit()
                    print(f"[OFFSEASON] ✅ Task 'Age Players' marked complete")
                else:
                    print(f"[OFFSEASON] ⚠️ Task 'Age Players' not found in offseason_tasks")
                
            except Exception as e:
                print(f"[OFFSEASON] ❌ Error marking task complete: {e}")
                import traceback
                traceback.print_exc()
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
            
            # Show success message
            details = result['details']
            QMessageBox.information(
                self,
                "Players Aged Successfully! ✅",
                f"All {result['players_aged']} players have been aged by 1 year.\n\n"
                f"📊 League Statistics:\n"
                f"• Average Age: {details['before']['avg_age']} → {details['after']['avg_age']}\n"
                f"• Youngest Player: {details['after']['youngest']} years old\n"
                f"• Oldest Player: {details['after']['oldest']} years old\n"
                f"• Players 35+: {details['after']['age_35_plus']}\n\n"
                f"Next: Consider processing retirements for older players."
            )
            
        else:
            QMessageBox.critical(
                self,
                "Error Aging Players",
                f"Failed to age players:\n\n{result['error']}"
            )
    
    def update_player_skills(self):
        """Update player skills based on age and position"""
        if not update_player_skills:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                "Update Skills utility not found.\n\n"
                "Make sure utils/update_skills.py exists."
            )
            return
        
        # Check if task already complete
        conn = None
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT is_complete FROM offseason_tasks
                WHERE league_id = ? AND from_season = ? AND task_name = 'Update Player Skills'
            """, (self.current_league_id, self.current_season))
            
            task = cursor.fetchone()
            if task:
                is_complete = task['is_complete'] if isinstance(task, dict) or hasattr(task, 'keys') else task[0]
                if is_complete:
                    reply = QMessageBox.question(
                        self,
                        "Task Already Complete",
                        "Player skills have already been updated for this season.\n\n"
                        "Do you want to update them again?\n"
                        "(This will apply additional skill changes)",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
        except Exception as e:
            print(f"[OFFSEASON] Warning checking task status: {e}")
        finally:
            if conn:
                conn.close()
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Update Player Skills?",
            f"Update skills for all players in Season {self.current_season}?\n\n"
            "This will:\n"
            "• Young players may improve\n"
            "• Prime players maintain or improve slightly\n"
            "• Aging players will decline\n"
            "• Changes based on age and position\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            print(f"[OFFSEASON] User cancelled skill updates")
            return
        
        print(f"[OFFSEASON] Starting player skill updates...")
        
        # Import and call the utility function
        from utils.update_skills import update_player_skills as do_update
        result = do_update(self.db_manager.db_path, self.current_league_id, self.current_season)
        
        if result['success']:
            # Mark task complete
            conn = None
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_manager.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                metadata = {
                    'players_updated': result['players_updated'],
                    'total_improvements': result['details']['total_improvements'],
                    'total_declines': result['details']['total_declines'],
                    'completed_date': datetime.now().isoformat()
                }
                
                cursor.execute("""
                    UPDATE offseason_tasks
                    SET is_complete = 1,
                        completed_date = ?,
                        completed_by = 'USER',
                        task_metadata = ?
                    WHERE league_id = ? AND from_season = ? AND task_name = 'Update Player Skills'
                """, (
                    datetime.now().isoformat(),
                    json.dumps(metadata),
                    self.current_league_id,
                    self.current_season
                ))
                
                conn.commit()
                print(f"[OFFSEASON] ✅ Task 'Update Player Skills' marked complete")
                
            except Exception as e:
                print(f"[OFFSEASON] ❌ Error marking task complete: {e}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
            
            # Show success message
            details = result['details']
            QMessageBox.information(
                self,
                "Skills Updated Successfully! ✅",
                f"{result['players_updated']} players had skill changes.\n\n"
                f"📊 Summary:\n"
                f"• Skills Improved: {details['total_improvements']}\n"
                f"• Skills Declined: {details['total_declines']}\n"
                f"• Net Change: {details['total_improvements'] - details['total_declines']:+d}\n\n"
                f"Average Skills:\n"
                f"• Run: {details['avg_skills']['run']}\n"
                f"• Pass: {details['avg_skills']['pass']}\n"
                f"• Receive: {details['avg_skills']['receive']}\n"
                f"• Block: {details['avg_skills']['block']}\n"
                f"• Kick: {details['avg_skills']['kick']}"
            )
            
        else:
            QMessageBox.critical(
                self,
                "Error Updating Skills",
                f"Failed to update player skills:\n\n{result['error']}"
            )
    
    def show_stub_message(self, feature_name):
        """Show placeholder message for stub features"""
        QMessageBox.information(
            self,
            "Feature Coming Soon",
            f"{feature_name} will be implemented in a future update.\n\n"
            "This feature is currently under development."
        )
