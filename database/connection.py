# ========================================
# database/connection.py
# ========================================

import sqlite3
import os
from typing import Optional


class DatabaseManager:
    """Manages database connections and basic operations"""
    
    def __init__(self, db_path: str = "pynfl.db"):
        self.db_path = db_path
        self._connection = None
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        if self._connection is None or not self._connection:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
        
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a SELECT query and return results"""
        # TODO: Implement query execution
        pass
        
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return rows affected"""
        # TODO: Implement update execution
        pass
        
    def get_current_league(self) -> Optional[dict]:
        """Get the currently active league"""
        # TODO: Get current league from database
        pass
        
    def get_current_season_week(self) -> tuple:
        """Get current season and week"""
        # TODO: Return (season, week) tuple
        pass
        
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
