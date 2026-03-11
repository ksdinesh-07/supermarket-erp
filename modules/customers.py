from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QTextEdit, QSpinBox, QMessageBox, QDialog,
                           QFormLayout, QFrame, QComboBox, QSplitter)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, validate_email, validate_phone
from datetime import datetime

class CustomersModule(QWidget):
    customer_updated = pyqtSignal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_customer = None
        self.init_ui()
        self.load_customers()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Customers list
        left_panel = self.create_customer_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Customer details
        right_panel = self.create_customer_details_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 400])
        layout.addWidget(splitter)
        
    def create_header(self):
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("👥 Customer Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search by name, phone, email...")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.load_customers)
        layout.addWidget(self.search_box)
        
        # Add customer button
        add_btn = QPushButton("➕ New Customer")
        add_btn.clicked.connect(self.new_customer)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(add_btn)
        
        return header
    
    def create_customer_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Loyalty Points", "Actions"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.itemClicked.connect(self.on_customer_selected)
        layout.addWidget(self.customers_table)
        
        return panel
    
    def create_customer_details_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Customer form
        form_group = QGroupBox("Customer Details")
        form_layout = QGridLayout()
        
        # Row 1
        form_layout.addWidget(QLabel("Name:*"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        form_layout.addWidget(self.name_input, 0, 1, 1, 2)
        
        # Row 2
        form_layout.addWidget(QLabel("Phone:*"), 1, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("10 digit mobile number")
        form_layout.addWidget(self.phone_input, 1, 1)
        
        form_layout.addWidget(QLabel("Email:"), 1, 2)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addWidget(self.email_input, 1, 3)
        
        # Row 3
        form_layout.addWidget(QLabel("Address:"), 2, 0)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form_layout.addWidget(self.address_input, 2, 1, 1, 3)
        
        # Row 4
        form_layout.addWidget(QLabel("Loyalty Points:"), 3, 0)
        self.loyalty_points = QSpinBox()
        self.loyalty_points.setRange(0, 999999)
        self.loyalty_points.setSingleStep(10)
        form_layout.addWidget(self.loyalty_points, 3, 1)
        
        form_layout.addWidget(QLabel("Member Since:"), 3, 2)
        self.member_since = QLabel(datetime.now().strftime('%d/%m/%Y'))
        form_layout.addWidget(self.member_since, 3, 3)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Purchase history summary
        history_group = QGroupBox("Purchase Summary")
        history_layout = QGridLayout()
        
        history_layout.addWidget(QLabel("Total Purchases:"), 0, 0)
        self.total_purchases = QLabel("0")
        history_layout.addWidget(self.total_purchases, 0, 1)
        
        history_layout.addWidget(QLabel("Total Spent:"), 0, 2)
        self.total_spent = QLabel("₹ 0.00")
        self.total_spent.setStyleSheet("color: #4CAF50; font-weight: bold;")
        history_layout.addWidget(self.total_spent, 0, 3)
        
        history_layout.addWidget(QLabel("Last Purchase:"), 1, 0)
        self.last_purchase = QLabel("Never")
        history_layout.addWidget(self.last_purchase, 1, 1)
        
        history_layout.addWidget(QLabel("Average Order:"), 1, 2)
        self.avg_order = QLabel("₹ 0.00")
        history_layout.addWidget(self.avg_order, 1, 3)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Recent purchases
        recent_group = QGroupBox("Recent Purchases")
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Date", "Invoice", "Amount"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_layout.addWidget(self.recent_table)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Customer")
        self.save_btn.clicked.connect(self.save_customer)
        self.save_btn.setStyleSheet("background-color: #2196F3;")
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_customer)
        self.delete_btn.setStyleSheet("background-color: #F44336;")
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("🔄 Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def load_customers(self):
        try:
            search = self.search_box.text()
            
            query = """
                SELECT c.*, 
                       COUNT(s.id) as purchase_count,
                       COALESCE(SUM(s.total_amount), 0) as total_spent,
                       MAX(s.created_at) as last_purchase_date
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (c.name LIKE %s OR c.phone LIKE %s OR c.email LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            query += " GROUP BY c.id ORDER BY c.name"
            
            customers = self.db.fetch_all(query, params)
            
            self.customers_table.setRowCount(len(customers))
            for i, customer in enumerate(customers):
                self.customers_table.setItem(i, 0, QTableWidgetItem(str(customer['id'])))
                self.customers_table.setItem(i, 1, QTableWidgetItem(customer['name']))
                self.customers_table.setItem(i, 2, QTableWidgetItem(customer['phone']))
                self.customers_table.setItem(i, 3, QTableWidgetItem(customer['email'] or '-'))
                
                points_item = QTableWidgetItem(str(customer['loyalty_points']))
                if customer['loyalty_points'] > 100:
                    points_item.setForeground(QColor('#4CAF50'))
                elif customer['loyalty_points'] > 50:
                    points_item.setForeground(QColor('#FF9800'))
                self.customers_table.setItem(i, 4, points_item)
                
                # View button
                view_btn = QPushButton("👁️ View")
                view_btn.clicked.connect(lambda checked, c=customer: self.view_customer(c))
                self.customers_table.setCellWidget(i, 5, view_btn)
                
        except Exception as e:
            print(f"Error loading customers: {e}")
    
    def on_customer_selected(self, item):
        row = item.row()
        customer_id = self.customers_table.item(row, 0).text()
        self.load_customer(customer_id)
    
    def load_customer(self, customer_id):
        try:
            query = """
                SELECT c.*, 
                       COUNT(s.id) as purchase_count,
                       COALESCE(SUM(s.total_amount), 0) as total_spent,
                       MAX(s.created_at) as last_purchase_date,
                       AVG(s.total_amount) as avg_order
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                WHERE c.id = %s
                GROUP BY c.id
            """
            customer = self.db.fetch_one(query, (customer_id,))
            
            if customer:
                self.current_customer = customer
                self.name_input.setText(customer['name'])
                self.phone_input.setText(customer['phone'])
                self.email_input.setText(customer['email'] or '')
                self.address_input.setText(customer['address'] or '')
                self.loyalty_points.setValue(customer['loyalty_points'])
                
                # Update purchase summary
                self.total_purchases.setText(str(customer['purchase_count']))
                self.total_spent.setText(format_currency(customer['total_spent']))
                
                if customer['last_purchase_date']:
                    if isinstance(customer['last_purchase_date'], datetime):
                        self.last_purchase.setText(customer['last_purchase_date'].strftime('%d/%m/%Y'))
                    else:
                        self.last_purchase.setText(str(customer['last_purchase_date']))
                else:
                    self.last_purchase.setText("Never")
                
                self.avg_order.setText(format_currency(customer['avg_order'] or 0))
                
                # Load recent purchases
                recent_query = """
                    SELECT invoice_number, created_at, total_amount
                    FROM sales
                    WHERE customer_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                recent = self.db.fetch_all(recent_query, (customer_id,))
                
                self.recent_table.setRowCount(len(recent))
                for i, sale in enumerate(recent):
                    if isinstance(sale['created_at'], datetime):
                        date_str = sale['created_at'].strftime('%d/%m/%Y')
                    else:
                        date_str = str(sale['created_at'])
                    self.recent_table.setItem(i, 0, QTableWidgetItem(date_str))
                    self.recent_table.setItem(i, 1, QTableWidgetItem(sale['invoice_number']))
                    self.recent_table.setItem(i, 2, QTableWidgetItem(format_currency(sale['total_amount'])))
                
                self.delete_btn.setEnabled(True)
                
        except Exception as e:
            print(f"Error loading customer: {e}")
    
    def new_customer(self):
        self.current_customer = None
        self.clear_form()
        self.delete_btn.setEnabled(False)
        self.name_input.setFocus()
    
    def clear_form(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.loyalty_points.setValue(0)
        self.total_purchases.setText("0")
        self.total_spent.setText("₹ 0.00")
        self.last_purchase.setText("Never")
        self.avg_order.setText("₹ 0.00")
        self.recent_table.setRowCount(0)
    
    def save_customer(self):
        # Validate
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation", "Customer name is required.")
            return
        
        if not phone:
            QMessageBox.warning(self, "Validation", "Phone number is required.")
            return
        
        if not validate_phone(phone):
            QMessageBox.warning(self, "Validation", "Please enter a valid 10-digit phone number.")
            return
        
        email = self.email_input.text().strip()
        if email and not validate_email(email):
            QMessageBox.warning(self, "Validation", "Please enter a valid email address.")
            return
        
        try:
            if self.current_customer:
                # Update existing customer
                query = """
                    UPDATE customers 
                    SET name = %s, phone = %s, email = %s, address = %s, loyalty_points = %s
                    WHERE id = %s
                """
                self.db.execute_query(query, (
                    name, phone, email or None,
                    self.address_input.toPlainText() or None,
                    self.loyalty_points.value(),
                    self.current_customer['id']
                ))
                
                QMessageBox.information(self, "Success", "Customer updated successfully!")
                
            else:
                # Check if phone exists
                check_query = "SELECT id FROM customers WHERE phone = %s"
                existing = self.db.fetch_one(check_query, (phone,))
                if existing:
                    QMessageBox.warning(self, "Duplicate", "Phone number already exists!")
                    return
                
                # Insert new customer
                query = """
                    INSERT INTO customers (name, phone, email, address, loyalty_points)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.db.execute_query(query, (
                    name, phone, email or None,
                    self.address_input.toPlainText() or None,
                    self.loyalty_points.value()
                ))
                
                QMessageBox.information(self, "Success", "Customer added successfully!")
            
            # Refresh
            self.load_customers()
            self.customer_updated.emit()
            self.new_customer()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer: {str(e)}")
    
    def delete_customer(self):
        if not self.current_customer:
            return
        
        # Check if customer has purchases
        check_query = "SELECT COUNT(*) as count FROM sales WHERE customer_id = %s"
        result = self.db.fetch_one(check_query, (self.current_customer['id'],))
        
        if result and result['count'] > 0:
            QMessageBox.warning(self, "Cannot Delete", 
                               "This customer has purchase history and cannot be deleted.")
            return
        
        reply = QMessageBox.question(self, "Delete Customer", 
                                    f"Are you sure you want to delete {self.current_customer['name']}?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM customers WHERE id = %s"
                self.db.execute_query(query, (self.current_customer['id'],))
                
                QMessageBox.information(self, "Success", "Customer deleted successfully!")
                self.load_customers()
                self.new_customer()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {str(e)}")
    
    def view_customer(self, customer):
        self.load_customer(customer['id'])
