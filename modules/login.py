from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from database.models import UserModel

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.current_user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Supermarket ERP - Login")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Title
        title_label = QLabel("🏪 Supermarket ERP")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Login to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(20)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setFont(QFont("Arial", 10))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        # Version info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: gray; font-size: 8pt;")
        layout.addStretch()
        layout.addWidget(version_label)
        
        self.setLayout(layout)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QPushButton {
                border-radius: 5px;
                background-color: #2196F3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        # Authenticate user
        user = self.user_model.authenticate(username, password)
        
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def get_user(self):
        return self.current_user
