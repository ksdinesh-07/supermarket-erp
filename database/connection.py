import pymysql
import pymysql.cursors
from config import DB_CONFIG

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Database connected successfully!")
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
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Query execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Exception as e:
            print(f"Fetch error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def fetch_one(self, query, params=None):
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Exception as e:
            print(f"Fetch error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
