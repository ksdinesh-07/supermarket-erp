import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from modules.login import LoginDialog
from database.connection import DatabaseConnection
from database.init_db import init_database

class SupermarketERP:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Supermarket ERP System")
        self.app.setApplicationVersion("1.0.0")
        
        # Initialize database (SQLite)
        self.init_database_if_needed()
        
        # Show splash screen
        self.show_splash()
        
        # Initialize database connection
        self.init_database_connection()
        
        # Show login dialog
        self.show_login()
    
    def init_database_if_needed(self):
        """Initialize SQLite database if it doesn't exist"""
        db_path = 'supermarket.db'
        if not os.path.exists(db_path):
            print("📦 First run detected. Creating database...")
            try:
                init_database()
                print("✅ Database created successfully!")
            except Exception as e:
                print(f"❌ Error creating database: {e}")
                QMessageBox.critical(None, "Database Error", 
                                   f"Failed to create database: {str(e)}")
        else:
            print(f"📦 Database found at: {db_path}")
    
    def show_splash(self):
        # Create a simple splash screen
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.white)
        self.splash = QSplashScreen(splash_pix)
        self.splash.show()
        self.splash.showMessage("Loading Supermarket ERP...", Qt.AlignBottom | Qt.AlignCenter, Qt.blue)
        QTimer.singleShot(2000, self.splash.close)
    
    def init_database_connection(self):
        try:
            self.db = DatabaseConnection()
            if self.db.connect():
                print("Database connected successfully!")
            else:
                QMessageBox.warning(None, "Database Warning", 
                                   "Could not connect to database.")
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Database error: {str(e)}")
    
    def show_login(self):
        self.login = LoginDialog()
        if self.login.exec_() == LoginDialog.Accepted:
            # Login successful, open main dashboard
            self.user = self.login.get_user()
            self.show_main_window()
        else:
            # User cancelled login, exit application
            sys.exit()
    
    def show_main_window(self):
        from modules.dashboard import MainDashboard
        self.dashboard = MainDashboard(self.user)
        self.dashboard.show()
    
    def run(self):
        return self.app.exec_()

if __name__ == "__main__":
    app = SupermarketERP()
    sys.exit(app.run())
