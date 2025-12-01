# ========================================
# common/widgets/data_grid.py
# ========================================

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


class DataGrid(QTableWidget):
    """Reusable data grid widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_grid()
        
    def setup_grid(self):
        """Setup grid appearance and behavior"""
        # TODO: Configure grid properties
        pass
        
    def load_data(self, data: list, headers: list):
        """Load data into the grid"""
        # TODO: Populate grid with data
        pass
        
    def get_selected_row_data(self) -> dict:
        """Get data from selected row"""
        # TODO: Return selected row as dictionary
        pass


