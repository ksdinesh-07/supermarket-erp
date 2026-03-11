import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from modules.login import LoginDialog
from database.connection import DatabaseConnection

class SupermarketERP:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Supermarket ERP System")
        self.app.setApplicationVersion("1.0.0")
        
        # Set application icon (you can add an icon file later)
        # self.app.setWindowIcon(QIcon('ui/resources/app_icon.png'))
        
        # Show splash screen
        self.show_splash()
        
        # Initialize database connection
        self.init_database()
        
        # Show login dialog
        self.show_login()
    
    def show_splash(self):
        # Create a simple splash screen
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.white)
        self.splash = QSplashScreen(splash_pix)
        self.splash.show()
        self.splash.showMessage("Loading Supermarket ERP...", Qt.AlignBottom | Qt.AlignCenter, Qt.blue)
        QTimer.singleShot(2000, self.splash.close)
    
    def init_database(self):
        try:
            db = DatabaseConnection()
            if db.connect():
                print("Database initialized successfully")
            else:
                QMessageBox.warning(None, "Database Warning", 
                                   "Could not connect to database. Please check your MySQL connection.")
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
        
        # Get screen size and set window to fit
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.9)  # 90% of screen width
        height = int(screen.height() * 0.9)  # 90% of screen height
        
        self.dashboard.resize(width, height)
        
        # Center the window
        frame_geometry = self.dashboard.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.dashboard.move(frame_geometry.topLeft())
        
        self.dashboard.show()
        self.dashboard.showMaximized()  # Start maximized for best fit
    
    def run(self):
        return self.app.exec_()

if __name__ == "__main__":
    app = SupermarketERP()
    sys.exit(app.run())
