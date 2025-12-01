# ========================================
# tabs/transactions/transactions_tab.py
# ========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class TransactionsTab(QWidget):
    """Transactions management tab"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize transactions tab UI"""
        layout = QVBoxLayout(self)
        
        title = QLabel("Transactions")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # TODO: Add transaction list, transaction entry components

