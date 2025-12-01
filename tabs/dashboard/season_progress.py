# ========================================
# tabs/dashboard/season_progress.py
# Version: 1.2 - Compact Layout
# ========================================

"""
Compact Season Progress Widget

Displays current season and week information in a minimal layout to save space.
Focuses on functionality over fancy styling to maximize room for content.

Features:
- Compact horizontal layout
- Small progress indicator
- Week navigation controls
- Minimal visual footprint
"""

import sqlite3
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QPushButton, QComboBox, QGroupBox, QMessageBox,
                            QProgressBar, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class SeasonProgressWidget(QWidget):
    """Compact widget for displaying and navigating season progress"""
    
    # Signal emitted when week changes: (season, week)
    week_changed = pyqtSignal(int, int)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_league_id = None
        self.current_season = 1
        self.current_week = 1
        self.max_weeks = 17  # Default
        self.games_completed = 0
        self.total_games = 0
        self.init_ui()
        self.load_league_info()
    
    def init_ui(self):
        """Initialize the compact season progress UI"""
        # Main horizontal layout - very compact
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(15)
        
        # Season info - compact
        season_label = QLabel(f"Season {self.current_season}")
        season_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            padding: 4px 8px;
            background: #ecf0f1;
            border-radius: 4px;
        """)
        main_layout.addWidget(season_label)
        self.season_display = season_label
        
        # Week navigation - compact horizontal layout
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)
        
        # Previous week button - smaller
        self.prev_week_btn = QPushButton("◀")
        self.prev_week_btn.setToolTip("Previous week")
        self.prev_week_btn.clicked.connect(self.prev_week)
        self.prev_week_btn.setFixedSize(30, 25)
        self.prev_week_btn.setStyleSheet("""
            QPushButton {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e9ecef;
                border-color: #74b9ff;
            }
            QPushButton:disabled {
                background: #f5f6fa;
                color: #a4b0be;
            }
        """)
        nav_layout.addWidget(self.prev_week_btn)
        
        # Week display and selector - compact
        week_container = QFrame()
        week_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        week_layout = QHBoxLayout(week_container)
        week_layout.setContentsMargins(8, 2, 8, 2)
        week_layout.setSpacing(5)
        
        self.week_label = QLabel("Week 1")
        self.week_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #2c3e50;
        """)
        week_layout.addWidget(self.week_label)
        
        # Small progress bar with more horizontal room
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setFixedWidth(120)  # Increased from 60 to 120px
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: #ecf0f1;
            }
            QProgressBar::chunk {
                background: #27ae60;
                border-radius: 2px;
            }
        """)
        week_layout.addWidget(self.progress_bar)
        
        nav_layout.addWidget(week_container)
        
        # Week selector - smaller
        self.week_combo = QComboBox()
        self.week_combo.setToolTip("Select week")
        self.week_combo.currentTextChanged.connect(self.week_selected)
        self.week_combo.setFixedHeight(25)
        self.week_combo.setStyleSheet("""
            QComboBox {
                padding: 2px 6px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-size: 11px;
                min-width: 70px;
                background: white;
            }
            QComboBox:hover {
                border-color: #74b9ff;
            }
        """)
        nav_layout.addWidget(self.week_combo)
        
        # Next week button - smaller
        self.next_week_btn = QPushButton("▶")
        self.next_week_btn.setToolTip("Next week")
        self.next_week_btn.clicked.connect(self.next_week)
        self.next_week_btn.setFixedSize(30, 25)
        self.next_week_btn.setStyleSheet("""
            QPushButton {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e9ecef;
                border-color: #74b9ff;
            }
            QPushButton:disabled {
                background: #f5f6fa;
                color: #a4b0be;
            }
        """)
        nav_layout.addWidget(self.next_week_btn)
        
        main_layout.addLayout(nav_layout)
        main_layout.addStretch()
        
        # Compact games info
        self.games_info_label = QLabel("0/0 games")
        self.games_info_label.setStyleSheet("""
            font-size: 10px;
            color: #7f8c8d;
            padding: 2px 6px;
            background: #f8f9fa;
            border-radius: 3px;
        """)
        main_layout.addWidget(self.games_info_label)
        
        # League info - very compact
        self.league_label = QLabel("No League")
        self.league_label.setStyleSheet("""
            font-size: 10px;
            color: #95a5a6;
            padding: 2px 6px;
        """)
        main_layout.addWidget(self.league_label)
        
        # Set maximum height to keep it compact
        self.setMaximumHeight(40)
    
    def load_league_info(self):
        """Load current league information and calculate progress"""
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
                
                # Calculate max weeks
                regular_weeks = result['regular_season_games'] or 17
                preseason_weeks = result['preseason_games'] or 0
                playoff_weeks = result['playoff_weeks'] or 4
                self.max_weeks = regular_weeks + playoff_weeks
                
                # Update UI
                self.season_display.setText(f"Season {self.current_season}")
                self.league_label.setText(result['league_name'] or "No League")
                
                # Calculate games completed
                self.calculate_games_progress()
                
                # Populate week selector
                self.populate_week_selector()
                self.update_week_display()
                
            else:
                self.league_label.setText("No League")
                print("No active league found")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading league info: {str(e)}")
            print(f"Error loading league info: {e}")
    
    def calculate_games_progress(self):
        """Calculate how many games have been completed this season"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Count completed games through current week
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN game_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_games
                FROM games 
                WHERE league_id = ? AND season = ? AND week <= ?
            """, (self.current_league_id, self.current_season, self.current_week))
            
            result = cursor.fetchone()
            if result:
                self.total_games = result['total_games'] or 0
                self.games_completed = result['completed_games'] or 0
            else:
                self.total_games = 0
                self.games_completed = 0
                
        except Exception as e:
            print(f"Error calculating games progress: {e}")
            self.total_games = 0
            self.games_completed = 0
    
    def populate_week_selector(self):
        """Populate the week selector combo box"""
        self.week_combo.blockSignals(True)
        self.week_combo.clear()
        
        for week in range(1, self.max_weeks + 1):
            self.week_combo.addItem(f"Week {week}", week)
        
        # Set current week
        for i in range(self.week_combo.count()):
            if self.week_combo.itemData(i) == self.current_week:
                self.week_combo.setCurrentIndex(i)
                break
        
        self.week_combo.blockSignals(False)
    
    def update_week_display(self):
        """Update the week display, progress bar, and button states"""
        self.week_label.setText(f"Week {self.current_week}")
        
        # Calculate progress percentage
        if self.max_weeks > 0:
            week_progress = (self.current_week / self.max_weeks) * 100
            self.progress_bar.setValue(int(week_progress))
        else:
            self.progress_bar.setValue(0)
        
        # Update games info - compact format
        self.games_info_label.setText(f"{self.games_completed}/{self.total_games} games")
        
        # Update button states
        self.prev_week_btn.setEnabled(self.current_week > 1)
        self.next_week_btn.setEnabled(self.current_week < self.max_weeks)
        
        # Update combo box selection
        self.week_combo.blockSignals(True)
        for i in range(self.week_combo.count()):
            if self.week_combo.itemData(i) == self.current_week:
                self.week_combo.setCurrentIndex(i)
                break
        self.week_combo.blockSignals(False)
    
    def prev_week(self):
        """Go to previous week"""
        if self.current_week > 1:
            self.set_week(self.current_week - 1)
    
    def next_week(self):
        """Go to next week"""
        if self.current_week < self.max_weeks:
            self.set_week(self.current_week + 1)
    
    def week_selected(self):
        """Handle week selection from combo box"""
        selected_week = self.week_combo.currentData()
        if selected_week and selected_week != self.current_week:
            self.set_week(selected_week)
    
    def set_week(self, week: int):
        """Set the current week and emit signal"""
        if 1 <= week <= self.max_weeks:
            self.current_week = week
            self.calculate_games_progress()  # Recalculate for new week
            self.update_week_display()
            self.week_changed.emit(self.current_season, self.current_week)
            print(f"Week changed to: Season {self.current_season}, Week {self.current_week}")
    
    def get_current_season_week(self) -> tuple:
        """Get current season and week"""
        return (self.current_season, self.current_week)
    
    def refresh(self):
        """Refresh the widget by reloading league info"""
        self.load_league_info()
