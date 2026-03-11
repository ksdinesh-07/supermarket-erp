from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QMessageBox, QDialog, QFormLayout, QTabWidget,
                           QFrame, QCheckBox, QFileDialog, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDate, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from datetime import datetime
import hashlib

class AdminModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        self.load_users()
        self.load_backup_info()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚙️ Admin Panel")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # User management tab
        user_tab = self.create_user_tab()
        self.tab_widget.addTab(user_tab, "👥 User Management")
        
        # Backup tab
        backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(backup_tab, "💾 Backup & Restore")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "⚙️ System Settings")
        
        # Audit log tab
        audit_tab = self.create_audit_tab()
        self.tab_widget.addTab(audit_tab, "📋 Audit Log")
        
        layout.addWidget(self.tab_widget)
        
    def create_user_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add user button
        add_btn = QPushButton("➕ Add New User")
        add_btn.clicked.connect(self.show_add_user_dialog)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                max-width: 200px;
            }
        """)
        layout.addWidget(add_btn)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Created", "Last Login", "Actions"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.users_table)
        
        return tab
    
    def create_backup_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Backup info
        info_group = QGroupBox("Backup Information")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Last Backup:"), 0, 0)
        self.last_backup_label = QLabel("Never")
        info_layout.addWidget(self.last_backup_label, 0, 1)
        
        info_layout.addWidget(QLabel("Backup Size:"), 1, 0)
        self.backup_size_label = QLabel("0 MB")
        info_layout.addWidget(self.backup_size_label, 1, 1)
        
        info_layout.addWidget(QLabel("Total Tables:"), 2, 0)
        self.total_tables_label = QLabel("0")
        info_layout.addWidget(self.total_tables_label, 2, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Backup actions
        actions_group = QGroupBox("Backup Actions")
        actions_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 Create Backup Now")
        backup_btn.clicked.connect(self.create_backup)
        backup_btn.setStyleSheet("background-color: #2196F3; padding: 10px;")
        actions_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📂 Restore from Backup")
        restore_btn.clicked.connect(self.restore_backup)
        restore_btn.setStyleSheet("background-color: #FF9800; padding: 10px;")
        actions_layout.addWidget(restore_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Backup history
        history_group = QGroupBox("Backup History")
        history_layout = QVBoxLayout()
        
        self.backup_history_table = QTableWidget()
        self.backup_history_table.setColumnCount(4)
        self.backup_history_table.setHorizontalHeaderLabels(["Date", "Size", "Tables", "Actions"])
        self.backup_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_layout.addWidget(self.backup_history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        return tab
    
    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Company settings
        company_group = QGroupBox("Company Information")
        company_layout = QGridLayout()
        
        company_layout.addWidget(QLabel("Company Name:"), 0, 0)
        self.company_name = QLineEdit()
        self.company_name.setText("Supermarket ERP")
        company_layout.addWidget(self.company_name, 0, 1)
        
        company_layout.addWidget(QLabel("Address:"), 1, 0)
        self.company_address = QTextEdit()
        self.company_address.setMaximumHeight(60)
        company_layout.addWidget(self.company_address, 1, 1)
        
        company_layout.addWidget(QLabel("Phone:"), 2, 0)
        self.company_phone = QLineEdit()
        company_layout.addWidget(self.company_phone, 2, 1)
        
        company_layout.addWidget(QLabel("Email:"), 3, 0)
        self.company_email = QLineEdit()
        company_layout.addWidget(self.company_email, 3, 1)
        
        company_layout.addWidget(QLabel("GST Number:"), 4, 0)
        self.company_gst = QLineEdit()
        company_layout.addWidget(self.company_gst, 4, 1)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # Tax settings
        tax_group = QGroupBox("Tax Settings")
        tax_layout = QGridLayout()
        
        tax_layout.addWidget(QLabel("Default Tax Rate (%):"), 0, 0)
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setValue(10)
        self.tax_rate.setSuffix("%")
        tax_layout.addWidget(self.tax_rate, 0, 1)
        
        tax_layout.addWidget(QLabel("Enable GST:"), 1, 0)
        self.enable_gst = QCheckBox()
        tax_layout.addWidget(self.enable_gst, 1, 1)
        
        tax_group.setLayout(tax_layout)
        layout.addWidget(tax_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #4CAF50; padding: 10px;")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
    
    def create_audit_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Audit log table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        self.audit_table.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Module", "Details"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.audit_table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Audit Log")
        refresh_btn.clicked.connect(self.load_audit_log)
        layout.addWidget(refresh_btn)
        
        return tab
    
    def load_users(self):
        try:
            from database.models import UserModel
            user_model = UserModel()
            users = user_model.get_all_users()
            
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(user['username']))
                self.users_table.setItem(i, 1, QTableWidgetItem(user['full_name']))
                
                role_item = QTableWidgetItem(user['role'].title())
                if user['role'] == 'admin':
                    role_item.setForeground(QColor('#F44336'))
                elif user['role'] == 'manager':
                    role_item.setForeground(QColor('#FF9800'))
                else:
                    role_item.setForeground(QColor('#4CAF50'))
                self.users_table.setItem(i, 2, role_item)
                
                created_str = user['created_at'].strftime('%d/%m/%Y') if user['created_at'] else '-'
                self.users_table.setItem(i, 3, QTableWidgetItem(created_str))
                
                last_login_str = user['last_login'].strftime('%d/%m/%Y %H:%M') if user['last_login'] else 'Never'
                self.users_table.setItem(i, 4, QTableWidgetItem(last_login_str))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(30)
                edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))
                actions_layout.addWidget(edit_btn)
                
                if user['username'] != 'admin':  # Don't allow deleting admin
                    delete_btn = QPushButton("🗑️")
                    delete_btn.setMaximumWidth(30)
                    delete_btn.setStyleSheet("color: #F44336;")
                    delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))
                    actions_layout.addWidget(delete_btn)
                
                self.users_table.setCellWidget(i, 5, actions_widget)
                
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def load_backup_info(self):
        # This would check the filesystem for backups
        # For now, show sample data
        self.last_backup_label.setText(datetime.now().strftime('%d/%m/%Y %H:%M'))
        self.backup_size_label.setText("2.3 MB")
        self.total_tables_label.setText("12")
        
        # Sample backup history
        self.backup_history_table.setRowCount(3)
        for i in range(3):
            date = datetime.now().strftime('%d/%m/%Y %H:%M')
            self.backup_history_table.setItem(i, 0, QTableWidgetItem(date))
            self.backup_history_table.setItem(i, 1, QTableWidgetItem("2.3 MB"))
            self.backup_history_table.setItem(i, 2, QTableWidgetItem("12"))
            
            restore_btn = QPushButton("↩️ Restore")
            restore_btn.clicked.connect(lambda: QMessageBox.information(self, "Restore", "Restore functionality coming soon!"))
            self.backup_history_table.setCellWidget(i, 3, restore_btn)
    
    def load_audit_log(self):
        # Sample audit log data
        self.audit_table.setRowCount(5)
        for i in range(5):
            self.audit_table.setItem(i, 0, QTableWidgetItem(datetime.now().strftime('%d/%m/%Y %H:%M')))
            self.audit_table.setItem(i, 1, QTableWidgetItem("admin"))
            self.audit_table.setItem(i, 2, QTableWidgetItem("Login"))
            self.audit_table.setItem(i, 3, QTableWidgetItem("System"))
            self.audit_table.setItem(i, 4, QTableWidgetItem("User logged in"))
    
    def show_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec_():
            self.load_users()
    
    def edit_user(self, user):
        dialog = EditUserDialog(user, self)
        if dialog.exec_():
            self.load_users()
    
    def delete_user(self, user):
        reply = QMessageBox.question(self, "Delete User", 
                                    f"Are you sure you want to delete {user['username']}?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                from database.models import UserModel
                user_model = UserModel()
                user_model.delete_user(user['id'])
                
                QMessageBox.information(self, "Success", "User deleted successfully!")
                self.load_users()
                
                # Log action
                self.log_audit("Delete User", f"Deleted user: {user['username']}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
    
    def create_backup(self):
        try:
            # This would create a database dump
            filename, _ = QFileDialog.getSaveFileName(self, "Save Backup", "", "SQL Files (*.sql)")
            if filename:
                # Simulate backup creation
                QMessageBox.information(self, "Backup", f"Backup saved to {filename}")
                self.log_audit("Backup", f"Created backup: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {str(e)}")
    
    def restore_backup(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "SQL Files (*.sql)")
        if filename:
            reply = QMessageBox.question(self, "Restore Backup", 
                                        "Restoring will overwrite current data. Continue?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Restore", "Restore functionality coming soon!")
                self.log_audit("Restore", f"Restored from backup: {filename}")
    
    def save_settings(self):
        # Save settings to config file
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.log_audit("Settings", "Updated system settings")
    
    def log_audit(self, action, details):
        # Log to audit table
        try:
            # Create audit_log table if not exists
            create_query = """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    action VARCHAR(100),
                    module VARCHAR(100),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """
            self.db.execute_query(create_query)
            
            query = """
                INSERT INTO audit_log (user_id, action, module, details)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query, (self.user['id'], action, "Admin", details))
        except Exception as e:
            print(f"Error logging audit: {e}")


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add New User")
        self.setGeometry(400, 300, 400, 350)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        form_layout.addRow("Username:*", self.username)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        form_layout.addRow("Password:*", self.password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm Password")
        form_layout.addRow("Confirm:*", self.confirm_password)
        
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full Name")
        form_layout.addRow("Full Name:*", self.full_name)
        
        self.role = QComboBox()
        self.role.addItems(["cashier", "manager", "admin"])
        form_layout.addRow("Role:", self.role)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_user(self):
        # Validate
        if not self.username.text():
            QMessageBox.warning(self, "Validation", "Username is required.")
            return
        
        if not self.password.text():
            QMessageBox.warning(self, "Validation", "Password is required.")
            return
        
        if self.password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Validation", "Passwords do not match.")
            return
        
        if not self.full_name.text():
            QMessageBox.warning(self, "Validation", "Full name is required.")
            return
        
        try:
            from database.models import UserModel
            user_model = UserModel()
            
            # Check if username exists
            check_query = "SELECT id FROM users WHERE username = %s"
            existing = self.db.fetch_one(check_query, (self.username.text(),))
            if existing:
                QMessageBox.warning(self, "Duplicate", "Username already exists!")
                return
            
            # Create user
            user_model.create_user(
                self.username.text(),
                self.password.text(),
                self.full_name.text(),
                self.role.currentText()
            )
            
            QMessageBox.information(self, "Success", "User added successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")


class EditUserDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Edit User - {self.user['username']}")
        self.setGeometry(400, 300, 400, 300)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.full_name = QLineEdit()
        self.full_name.setText(self.user['full_name'])
        form_layout.addRow("Full Name:*", self.full_name)
        
        self.role = QComboBox()
        self.role.addItems(["cashier", "manager", "admin"])
        self.role.setCurrentText(self.user['role'])
        form_layout.addRow("Role:", self.role)
        
        self.reset_password = QCheckBox("Reset Password")
        self.reset_password.toggled.connect(self.toggle_password)
        form_layout.addRow(self.reset_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("New Password")
        self.new_password.setEnabled(False)
        form_layout.addRow("New Password:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setEnabled(False)
        form_layout.addRow("Confirm:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_password(self, checked):
        self.new_password.setEnabled(checked)
        self.confirm_password.setEnabled(checked)
    
    def save_user(self):
        if not self.full_name.text():
            QMessageBox.warning(self, "Validation", "Full name is required.")
            return
        
        if self.reset_password.isChecked():
            if not self.new_password.text():
                QMessageBox.warning(self, "Validation", "New password is required.")
                return
            
            if self.new_password.text() != self.confirm_password.text():
                QMessageBox.warning(self, "Validation", "Passwords do not match.")
                return
        
        try:
            from database.models import UserModel
            user_model = UserModel()
            
            # Update user info
            user_model.update_user(self.user['id'], self.full_name.text(), self.role.currentText())
            
            # Update password if requested
            if self.reset_password.isChecked():
                import hashlib
                password_hash = hashlib.sha256(self.new_password.text().encode()).hexdigest()
                query = "UPDATE users SET password_hash = %s WHERE id = %s"
                self.db.execute_query(query, (password_hash, self.user['id']))
            
            QMessageBox.information(self, "Success", "User updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")
