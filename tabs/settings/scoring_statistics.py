# ========================================
# tabs/settings/scoring_statistics.py
# ========================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox,
                            QPushButton, QDoubleSpinBox, QTabWidget)


class ScoringStatisticsPanel(QWidget):
    """Scoring and statistics settings panel"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize scoring and statistics UI"""
        layout = QVBoxLayout(self)
        
        # Panel title
        title = QLabel("Scoring & Statistics")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tabbed interface for different categories
        self.settings_tabs = QTabWidget()
        
        # Scoring tab
        scoring_tab = QWidget()
        scoring_layout = QVBoxLayout(scoring_tab)
        
        # Touchdown scoring
        td_group = QGroupBox("Touchdown Scoring")
        td_layout = QFormLayout(td_group)
        
        self.rushing_td_spin = QSpinBox()
        self.rushing_td_spin.setRange(1, 10)
        self.rushing_td_spin.setValue(6)
        td_layout.addRow("Rushing TD:", self.rushing_td_spin)
        
        self.passing_td_spin = QSpinBox()
        self.passing_td_spin.setRange(1, 10)
        self.passing_td_spin.setValue(6)
        td_layout.addRow("Passing TD:", self.passing_td_spin)
        
        self.receiving_td_spin = QSpinBox()
        self.receiving_td_spin.setRange(1, 10)
        self.receiving_td_spin.setValue(6)
        td_layout.addRow("Receiving TD:", self.receiving_td_spin)
        
        scoring_layout.addWidget(td_group)
        
        # Field goal scoring
        fg_group = QGroupBox("Field Goal Scoring")
        fg_layout = QFormLayout(fg_group)
        
        self.fg_0_30_spin = QSpinBox()
        self.fg_0_30_spin.setRange(1, 5)
        self.fg_0_30_spin.setValue(3)
        fg_layout.addRow("0-30 yards:", self.fg_0_30_spin)
        
        self.fg_31_40_spin = QSpinBox()
        self.fg_31_40_spin.setRange(1, 5)
        self.fg_31_40_spin.setValue(3)
        fg_layout.addRow("31-40 yards:", self.fg_31_40_spin)
        
        self.fg_41_50_spin = QSpinBox()
        self.fg_41_50_spin.setRange(1, 5)
        self.fg_41_50_spin.setValue(3)
        fg_layout.addRow("41-50 yards:", self.fg_41_50_spin)
        
        self.fg_51_plus_spin = QSpinBox()
        self.fg_51_plus_spin.setRange(1, 6)
        self.fg_51_plus_spin.setValue(4)
        fg_layout.addRow("51+ yards:", self.fg_51_plus_spin)
        
        scoring_layout.addWidget(fg_group)
        scoring_layout.addStretch()
        
        self.settings_tabs.addTab(scoring_tab, "Scoring")
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # Stat tracking options
        tracking_group = QGroupBox("Statistics Tracking")
        tracking_layout = QVBoxLayout(tracking_group)
        
        self.track_individual_stats = QCheckBox("Track Individual Player Stats")
        self.track_individual_stats.setChecked(True)
        
        self.track_team_stats = QCheckBox("Track Team Statistics")
        self.track_team_stats.setChecked(True)
        
        self.track_advanced_stats = QCheckBox("Track Advanced Statistics")
        
        self.track_historical_stats = QCheckBox("Maintain Historical Statistics")
        self.track_historical_stats.setChecked(True)
        
        tracking_layout.addWidget(self.track_individual_stats)
        tracking_layout.addWidget(self.track_team_stats)
        tracking_layout.addWidget(self.track_advanced_stats)
        tracking_layout.addWidget(self.track_historical_stats)
        
        stats_layout.addWidget(tracking_group)
        
        # Stat calculation options
        calc_group = QGroupBox("Calculation Options")
        calc_layout = QFormLayout(calc_group)
        
        self.min_attempts_spin = QSpinBox()
        self.min_attempts_spin.setRange(1, 50)
        self.min_attempts_spin.setValue(10)
        calc_layout.addRow("Min Attempts for Averages:", self.min_attempts_spin)
        
        self.round_decimals_spin = QSpinBox()
        self.round_decimals_spin.setRange(1, 4)
        self.round_decimals_spin.setValue(2)
        calc_layout.addRow("Decimal Places:", self.round_decimals_spin)
        
        stats_layout.addWidget(calc_group)
        stats_layout.addStretch()
        
        self.settings_tabs.addTab(stats_tab, "Statistics")
        
        layout.addWidget(self.settings_tabs)
        
        # Save button
        button_layout = QHBoxLayout()
        self.save_scoring_btn = QPushButton("Save Scoring & Statistics Settings")
        button_layout.addWidget(self.save_scoring_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class TeamsTab(QWidget):
    """Teams management tab"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize teams tab UI"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Teams Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # TODO: Add team list, team details, roster view components

