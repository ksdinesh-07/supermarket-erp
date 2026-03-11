import sqlite3
import os
from datetime import datetime

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
            cls._instance.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'supermarket.db')
        return cls._instance
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Register custom functions for SQLite
            def regexp(pattern, item):
                return 1  # Simple implementation
            
            def curdate():
                return datetime.now().date().isoformat()
            
            def now():
                return datetime.now().isoformat()
            
            def date_sub(date_str, days):
                from datetime import datetime, timedelta
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    date_obj = datetime.now().date()
                return (date_obj - timedelta(days=int(days))).isoformat()
            
            self.connection.create_function("REGEXP", 2, regexp)
            self.connection.create_function("CURDATE", 0, curdate)
            self.connection.create_function("NOW", 0, now)
            self.connection.create_function("DATE_SUB", 2, date_sub)
            
            print(f"Database connected successfully at {self.db_path}")
            return self.connection
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Database disconnected!")
    
    def execute_query(self, query, params=None):
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            if params:
                # Convert any list/tuple params to appropriate format
                if isinstance(params, (list, tuple)):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, (params,))
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Query execution error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            if params:
                if isinstance(params, (list, tuple)):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, (params,))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Fetch error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return []
    
    def fetch_one(self, query, params=None):
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            if params:
                if isinstance(params, (list, tuple)):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, (params,))
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Exception as e:
            print(f"Fetch error: {e}")
            return None
    
    def table_exists(self, table_name):
        """Check if a table exists"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table_name,))
        return result is not None
