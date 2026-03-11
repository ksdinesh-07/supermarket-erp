from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QSpinBox, QDoubleSpinBox, QMessageBox, QDialog,
                           QFrame, QComboBox, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, generate_invoice_number
from datetime import datetime

class POSModule(QWidget):
    billing_completed = pyqtSignal(dict)
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.cart_items = []
        self.current_customer = None
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel - Product selection
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel, 1)
        
        # Right panel - Cart and payment
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel, 1)
        
    def create_left_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("🛒 Point of Sale")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(title)
        
        # Barcode input
        barcode_group = QGroupBox("Scan Barcode")
        barcode_layout = QVBoxLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan or enter barcode...")
        self.barcode_input.setFont(QFont("Arial", 14))
        self.barcode_input.setFixedHeight(40)
        self.barcode_input.returnPressed.connect(self.scan_barcode)
        barcode_layout.addWidget(self.barcode_input)
        
        barcode_group.setLayout(barcode_layout)
        layout.addWidget(barcode_group)
        
        # Quick products
        quick_group = QGroupBox("Quick Products")
        quick_layout = QGridLayout()
        
        quick_products = [
            ("🥛 Milk", "60", "1"),
            ("🍞 Bread", "40", "2"),
            ("🥚 Eggs", "80", "3"),
            ("🍚 Rice", "120", "4"),
            ("🫘 Dal", "110", "5"),
            ("🛢️ Oil", "130", "6"),
        ]
        
        for i, (name, price, idx) in enumerate(quick_products):
            row = i // 2
            col = i % 2
            btn = QPushButton(f"{name}\n₹{price}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #2196F3;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, p=price: self.add_quick_product(n, float(p)))
            quick_layout.addWidget(btn, row, col)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # Product search
        search_group = QGroupBox("Search Products")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(3)
        self.search_results.setHorizontalHeaderLabels(["Product", "Price", ""])
        self.search_results.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_results.setMaximumHeight(200)
        search_layout.addWidget(self.search_results)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        return panel
    
    def create_right_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        
        layout = QVBoxLayout(panel)
        
        # Customer selection
        customer_group = QGroupBox("Customer")
        customer_layout = QHBoxLayout()
        
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("Walk-in Customer", None)
        self.customer_combo.currentIndexChanged.connect(self.select_customer)
        customer_layout.addWidget(self.customer_combo, 1)
        
        self.new_customer_btn = QPushButton("➕ New")
        self.new_customer_btn.clicked.connect(self.show_new_customer_dialog)
        customer_layout.addWidget(self.new_customer_btn)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Cart
        cart_group = QGroupBox("Current Bill")
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        
        cart_group.setLayout(cart_layout)
        layout.addWidget(cart_group)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QGridLayout()
        
        summary_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("₹ 0.00")
        self.subtotal_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.subtotal_label, 0, 1)
        
        summary_layout.addWidget(QLabel("Tax (10%):"), 1, 0)
        self.tax_label = QLabel("₹ 0.00")
        self.tax_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.tax_label, 1, 1)
        
        summary_layout.addWidget(QLabel("Total:"), 2, 0)
        self.total_label = QLabel("₹ 0.00")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(self.total_label, 2, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Payment
        payment_group = QGroupBox("Payment")
        payment_layout = QFormLayout()
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "UPI"])
        payment_layout.addRow("Method:", self.payment_method)
        
        self.amount_paid = QDoubleSpinBox()
        self.amount_paid.setRange(0, 999999)
        self.amount_paid.setPrefix("₹ ")
        self.amount_paid.valueChanged.connect(self.calculate_change)
        payment_layout.addRow("Amount Paid:", self.amount_paid)
        
        self.change_label = QLabel("₹ 0.00")
        self.change_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.change_label.setStyleSheet("color: #4CAF50;")
        payment_layout.addRow("Change:", self.change_label)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_cart)
        button_layout.addWidget(self.clear_btn)
        
        self.payment_btn = QPushButton("💰 Complete Payment")
        self.payment_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.payment_btn.clicked.connect(self.complete_payment)
        button_layout.addWidget(self.payment_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def scan_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        query = "SELECT * FROM products WHERE barcode = %s"
        product = self.db.fetch_one(query, (barcode,))
        
        if product:
            self.add_to_cart(product)
            self.barcode_input.clear()
        else:
            QMessageBox.warning(self, "Not Found", f"No product found with barcode: {barcode}")
            self.barcode_input.clear()
    
    def add_quick_product(self, name, price):
        # Create a temporary product
        product = {
            'id': None,
            'name': name,
            'selling_price': price
        }
        self.add_to_cart(product)
    
    def search_products(self):
        search = self.search_input.text()
        if len(search) < 2:
            self.search_results.setRowCount(0)
            return
        
        query = "SELECT * FROM products WHERE name LIKE %s OR barcode LIKE %s LIMIT 10"
        search_term = f"%{search}%"
        products = self.db.fetch_all(query, (search_term, search_term))
        
        self.search_results.setRowCount(len(products))
        for i, product in enumerate(products):
            self.search_results.setItem(i, 0, QTableWidgetItem(product['name']))
            self.search_results.setItem(i, 1, QTableWidgetItem(format_currency(product['selling_price'])))
            
            add_btn = QPushButton("➕ Add")
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            self.search_results.setCellWidget(i, 2, add_btn)
    
    def add_to_cart(self, product):
        # Check if product already in cart
        for item in self.cart_items:
            if item.get('product_id') == product.get('id'):
                item['quantity'] += 1
                item['total'] = item['quantity'] * item['price']
                self.update_cart()
                return
        
        # Add new item
        self.cart_items.append({
            'product_id': product.get('id'),
            'product_name': product['name'],
            'quantity': 1,
            'price': float(product['selling_price']),
            'total': float(product['selling_price'])
        })
        
        self.update_cart()
    
    def update_cart(self):
        self.cart_table.setRowCount(len(self.cart_items))
        
        subtotal = 0
        for i, item in enumerate(self.cart_items):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            
            # Quantity with +/- buttons
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            
            minus_btn = QPushButton("-")
            minus_btn.setMaximumWidth(30)
            minus_btn.clicked.connect(lambda checked, idx=i: self.adjust_quantity(idx, -1))
            qty_layout.addWidget(minus_btn)
            
            qty_label = QLabel(str(item['quantity']))
            qty_label.setAlignment(Qt.AlignCenter)
            qty_layout.addWidget(qty_label)
            
            plus_btn = QPushButton("+")
            plus_btn.setMaximumWidth(30)
            plus_btn.clicked.connect(lambda checked, idx=i: self.adjust_quantity(idx, 1))
            qty_layout.addWidget(plus_btn)
            
            self.cart_table.setCellWidget(i, 1, qty_widget)
            
            self.cart_table.setItem(i, 2, QTableWidgetItem(format_currency(item['price'])))
            self.cart_table.setItem(i, 3, QTableWidgetItem(format_currency(item['total'])))
            
            remove_btn = QPushButton("✖")
            remove_btn.setMaximumWidth(30)
            remove_btn.setStyleSheet("background-color: #F44336; color: white;")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
            
            subtotal += item['total']
        
        # Update totals
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.subtotal_label.setText(format_currency(subtotal))
        self.tax_label.setText(format_currency(tax))
        self.total_label.setText(format_currency(total))
    
    def adjust_quantity(self, index, change):
        if 0 <= index < len(self.cart_items):
            new_qty = self.cart_items[index]['quantity'] + change
            if new_qty > 0:
                self.cart_items[index]['quantity'] = new_qty
                self.cart_items[index]['total'] = new_qty * self.cart_items[index]['price']
                self.update_cart()
            elif new_qty == 0:
                self.remove_item(index)
    
    def remove_item(self, index):
        if 0 <= index < len(self.cart_items):
            del self.cart_items[index]
            self.update_cart()
    
    def clear_cart(self):
        reply = QMessageBox.question(self, "Clear Cart", "Clear all items?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart()
    
    def calculate_change(self):
        total = float(self.total_label.text().replace('₹', '').replace(',', '').strip())
        paid = self.amount_paid.value()
        
        if paid >= total:
            change = paid - total
            self.change_label.setText(format_currency(change))
        else:
            self.change_label.setText("Insufficient")
    
    def select_customer(self):
        customer_id = self.customer_combo.currentData()
        if customer_id:
            query = "SELECT * FROM customers WHERE id = %s"
            self.current_customer = self.db.fetch_one(query, (customer_id,))
        else:
            self.current_customer = None
    
    def load_customers(self):
        query = "SELECT id, name, phone FROM customers ORDER BY name"
        customers = self.db.fetch_all(query)
        
        self.customer_combo.clear()
        self.customer_combo.addItem("Walk-in Customer", None)
        
        for customer in customers:
            self.customer_combo.addItem(f"{customer['name']} ({customer['phone']})", customer['id'])
    
    def show_new_customer_dialog(self):
        dialog = NewCustomerDialog(self)
        if dialog.exec_():
            self.load_customers()
    
    def complete_payment(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "No items in cart.")
            return
        
        total = float(self.total_label.text().replace('₹', '').replace(',', '').strip())
        method = self.payment_method.currentText().lower()
        
        if method == 'cash':
            paid = self.amount_paid.value()
            if paid < total:
                QMessageBox.warning(self, "Insufficient Payment", 
                                   f"Amount paid ({format_currency(paid)}) is less than total ({format_currency(total)})")
                return
        
        try:
            invoice = generate_invoice_number()
            
            # Insert sale
            sale_query = """
                INSERT INTO sales (invoice_number, user_id, customer_id, total_amount, tax, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            customer_id = self.current_customer['id'] if self.current_customer else None
            
            cursor = self.db.execute_query(sale_query, (
                invoice,
                self.user['id'],
                customer_id,
                total,
                total * 0.10,
                method
            ))
            
            if cursor:
                sale_id = cursor.lastrowid
                
                # Insert items
                for item in self.cart_items:
                    if item.get('product_id'):
                        item_query = """
                            INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        self.db.execute_query(item_query, (
                            sale_id,
                            item['product_id'],
                            item['quantity'],
                            item['price'],
                            item['total']
                        ))
                        
                        # Update stock
                        stock_query = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
                        self.db.execute_query(stock_query, (item['quantity'], item['product_id']))
                
                QMessageBox.information(self, "Success", f"Payment completed!\nInvoice: {invoice}")
                self.billing_completed.emit({'invoice': invoice, 'total': total})
                self.clear_cart()
                self.amount_paid.setValue(0)
                self.load_customers()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Payment failed: {str(e)}")


class NewCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("New Customer")
        self.setGeometry(400, 300, 400, 250)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Customer name")
        form_layout.addRow("Name:*", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone number")
        form_layout.addRow("Phone:*", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (optional)")
        form_layout.addRow("Email:", self.email_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_customer)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_customer(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Validation", "Name and phone are required.")
            return
        
        try:
            query = "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)"
            self.db.execute_query(query, (name, phone, self.email_input.text() or None))
            
            QMessageBox.information(self, "Success", "Customer added successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add customer: {str(e)}")
