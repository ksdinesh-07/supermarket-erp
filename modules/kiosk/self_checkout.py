from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QSpinBox, QDoubleSpinBox, QMessageBox, QDialog,
                           QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, generate_invoice_number
from datetime import datetime
import uuid

class SelfCheckoutKiosk(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_session = None
        self.cart_items = []
        self.kiosk_number = f"KIO-{str(uuid.uuid4())[:8]}"
        self.init_ui()
        self.create_session()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #2196F3; color: white; border-radius: 10px;")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("🛒 Self-Checkout Kiosk")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title)
        
        self.kiosk_label = QLabel(f"Kiosk: {self.kiosk_number}")
        self.kiosk_label.setFont(QFont("Arial", 12))
        header_layout.addWidget(self.kiosk_label)
        
        layout.addWidget(header)
        
        # Main content
        main_layout = QHBoxLayout()
        
        # Left panel - Product scanning
        left_panel = self.create_scanning_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Cart
        right_panel = self.create_cart_panel()
        main_layout.addWidget(right_panel, 1)
        
        layout.addLayout(main_layout)
        
        # Bottom panel - Payment
        bottom_panel = self.create_payment_panel()
        layout.addWidget(bottom_panel)
        
    def create_scanning_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📷 Scan Products")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        # Barcode input
        input_group = QGroupBox("Barcode Scanner")
        input_layout = QVBoxLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode or enter manually...")
        self.barcode_input.setFont(QFont("Arial", 14))
        self.barcode_input.setFixedHeight(50)
        self.barcode_input.returnPressed.connect(self.scan_barcode)
        input_layout.addWidget(self.barcode_input)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        self.add_manual_btn = QPushButton("🔍 Search Product")
        self.add_manual_btn.clicked.connect(self.search_product)
        quick_layout.addWidget(self.add_manual_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_input)
        quick_layout.addWidget(self.clear_btn)
        
        input_layout.addLayout(quick_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Recently scanned
        recent_group = QGroupBox("Recently Scanned")
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Product", "Price", "Time"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_layout.addWidget(self.recent_table)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        return panel
    
    def create_cart_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("🛍️ Your Cart")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        # Cart items
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Subtotal"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.cart_table)
        
        # Cart summary
        summary_group = QGroupBox("Summary")
        summary_layout = QGridLayout()
        
        self.item_count_label = QLabel("0 items")
        summary_layout.addWidget(QLabel("Items:"), 0, 0)
        summary_layout.addWidget(self.item_count_label, 0, 1)
        
        self.subtotal_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Subtotal:"), 1, 0)
        summary_layout.addWidget(self.subtotal_label, 1, 1)
        
        self.tax_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Tax (10%):"), 2, 0)
        summary_layout.addWidget(self.tax_label, 2, 1)
        
        self.total_label = QLabel("₹ 0.00")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(QLabel("Total:"), 3, 0)
        summary_layout.addWidget(self.total_label, 3, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        return panel
    
    def create_payment_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        panel.setFixedHeight(100)
        
        layout = QHBoxLayout(panel)
        
        # Payment methods
        methods_group = QGroupBox("Payment Method")
        methods_layout = QHBoxLayout()
        
        self.cash_btn = QPushButton("💵 Cash")
        self.cash_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.cash_btn.clicked.connect(lambda: self.process_payment('cash'))
        methods_layout.addWidget(self.cash_btn)
        
        self.card_btn = QPushButton("💳 Card")
        self.card_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.card_btn.clicked.connect(lambda: self.process_payment('card'))
        methods_layout.addWidget(self.card_btn)
        
        self.upi_btn = QPushButton("📱 UPI")
        self.upi_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.upi_btn.clicked.connect(lambda: self.process_payment('upi'))
        methods_layout.addWidget(self.upi_btn)
        
        methods_group.setLayout(methods_layout)
        layout.addWidget(methods_group)
        
        # Total amount
        total_frame = QFrame()
        total_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        total_layout = QVBoxLayout(total_frame)
        
        self.payment_total_label = QLabel("₹ 0.00")
        self.payment_total_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.payment_total_label.setStyleSheet("color: #2196F3;")
        total_layout.addWidget(self.payment_total_label)
        
        layout.addWidget(total_frame)
        
        return panel
    
    def create_session(self):
        try:
            session_id = str(uuid.uuid4())
            # Fixed: Changed %s to ? for SQLite
            query = """
                INSERT INTO kiosk_sessions (session_id, kiosk_number, status)
                VALUES (?, ?, 'active')
            """
            cursor = self.db.execute_query(query, (session_id, self.kiosk_number))
            if cursor:
                self.current_session = {
                    'session_id': session_id,
                    'id': cursor.lastrowid
                }
        except Exception as e:
            print(f"Error creating session: {e}")
    
    def scan_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        # Find product - Fixed: Changed %s to ?
        query = "SELECT * FROM products WHERE barcode = ?"
        product = self.db.fetch_one(query, (barcode,))
        
        if product:
            self.add_to_cart(product)
            self.add_to_recent(product)
            self.barcode_input.clear()
        else:
            QMessageBox.warning(self, "Not Found", f"No product found with barcode: {barcode}")
            self.barcode_input.clear()
    
    def add_to_cart(self, product):
        # Check if product already in cart
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                item['quantity'] += 1
                item['subtotal'] = item['quantity'] * item['price']
                self.update_cart_display()
                self.save_to_session(product['id'], 1)
                return
        
        # Add new item
        self.cart_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'quantity': 1,
            'price': float(product['selling_price']),
            'subtotal': float(product['selling_price'])
        })
        
        self.update_cart_display()
        self.save_to_session(product['id'], 1)
    
    def save_to_session(self, product_id, quantity):
        if self.current_session:
            # Fixed: Changed %s to ?
            query = """
                INSERT INTO kiosk_cart_items (session_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """
            self.db.execute_query(query, (
                self.current_session['id'],
                product_id,
                quantity,
                self.get_product_price(product_id)
            ))
    
    def get_product_price(self, product_id):
        # Fixed: Changed %s to ?
        query = "SELECT selling_price FROM products WHERE id = ?"
        result = self.db.fetch_one(query, (product_id,))
        return result['selling_price'] if result else 0
    
    def add_to_recent(self, product):
        # Add to recent table
        row = self.recent_table.rowCount()
        self.recent_table.insertRow(0)
        self.recent_table.setItem(0, 0, QTableWidgetItem(product['name']))
        self.recent_table.setItem(0, 1, QTableWidgetItem(format_currency(product['selling_price'])))
        from datetime import datetime
        self.recent_table.setItem(0, 2, QTableWidgetItem(datetime.now().strftime('%H:%M:%S')))
        
        # Keep only last 10 items
        if self.recent_table.rowCount() > 10:
            self.recent_table.removeRow(10)
    
    def update_cart_display(self):
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
            self.cart_table.setItem(i, 3, QTableWidgetItem(format_currency(item['subtotal'])))
            
            subtotal += item['subtotal']
        
        # Update summary
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.item_count_label.setText(f"{len(self.cart_items)} items")
        self.subtotal_label.setText(format_currency(subtotal))
        self.tax_label.setText(format_currency(tax))
        self.total_label.setText(format_currency(total))
        self.payment_total_label.setText(format_currency(total))
    
    def adjust_quantity(self, index, change):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['quantity'] += change
            if self.cart_items[index]['quantity'] <= 0:
                # Remove item
                del self.cart_items[index]
            else:
                # Update subtotal
                self.cart_items[index]['subtotal'] = self.cart_items[index]['quantity'] * self.cart_items[index]['price']
            
            self.update_cart_display()
            
            # Update session
            if self.current_session:
                # Delete old and insert new - Fixed: Changed %s to ?
                del_query = "DELETE FROM kiosk_cart_items WHERE session_id = ? AND product_id = ?"
                self.db.execute_query(del_query, (self.current_session['id'], self.cart_items[index]['product_id']))
                
                if self.cart_items[index]['quantity'] > 0:
                    self.save_to_session(self.cart_items[index]['product_id'], self.cart_items[index]['quantity'])
    
    def search_product(self):
        dialog = ProductSearchDialog(self)
        if dialog.exec_():
            product, quantity = dialog.get_selected_product()
            if product:
                for _ in range(quantity):
                    self.add_to_cart(product)
    
    def clear_input(self):
        self.barcode_input.clear()
    
    def process_payment(self, method):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart first.")
            return
        
        # Calculate totals
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        tax = subtotal * 0.10
        total = subtotal + tax
        
        # Create sale
        try:
            invoice = generate_invoice_number()
            
            # Insert sale - Fixed: Changed %s to ?
            sale_query = """
                INSERT INTO sales (invoice_number, user_id, total_amount, tax, billing_type, payment_method)
                VALUES (?, ?, ?, ?, 'self_checkout', ?)
            """
            cursor = self.db.execute_query(sale_query, (invoice, self.user['id'], total, tax, method))
            
            if cursor:
                sale_id = cursor.lastrowid
                
                # Insert items and update stock
                for item in self.cart_items:
                    # Fixed: Changed %s to ?
                    item_query = """
                        INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    self.db.execute_query(item_query, (
                        sale_id,
                        item['product_id'],
                        item['quantity'],
                        item['price'],
                        item['subtotal']
                    ))
                    
                    # Update stock - Fixed: Changed %s to ?
                    stock_query = "UPDATE products SET quantity = quantity - ? WHERE id = ?"
                    self.db.execute_query(stock_query, (item['quantity'], item['product_id']))
                
                # Update kiosk session - Fixed: Changed %s to ?
                update_query = "UPDATE kiosk_sessions SET status = 'completed', end_time = CURRENT_TIMESTAMP WHERE id = ?"
                self.db.execute_query(update_query, (self.current_session['id'],))
                
                # Show receipt
                self.show_receipt(invoice, subtotal, tax, total, method)
                
                # Clear cart and start new session
                self.cart_items = []
                self.update_cart_display()
                self.create_session()
                
        except Exception as e:
            QMessageBox.critical(self, "Payment Error", f"Failed to process payment: {str(e)}")
    
    def show_receipt(self, invoice, subtotal, tax, total, method):
        receipt = QDialog(self)
        receipt.setWindowTitle("Payment Successful")
        receipt.setGeometry(400, 300, 300, 400)
        
        layout = QVBoxLayout(receipt)
        
        # Header
        title = QLabel("🧾 RECEIPT")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Store info
        store = QLabel("Supermarket ERP")
        store.setAlignment(Qt.AlignCenter)
        layout.addWidget(store)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)
        
        # Invoice details
        layout.addWidget(QLabel(f"Invoice: {invoice}"))
        from datetime import datetime
        layout.addWidget(QLabel(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
        layout.addWidget(QLabel(f"Kiosk: {self.kiosk_number}"))
        
        layout.addWidget(QLabel(f"Payment: {method.upper()}"))
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider2)
        
        # Summary
        layout.addWidget(QLabel(f"Subtotal: {format_currency(subtotal)}"))
        layout.addWidget(QLabel(f"Tax (10%): {format_currency(tax)}"))
        
        total_label = QLabel(f"TOTAL: {format_currency(total)}")
        total_label.setFont(QFont("Arial", 14, QFont.Bold))
        total_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(total_label)
        
        # Thank you
        thanks = QLabel("\nThank you for shopping!")
        thanks.setAlignment(Qt.AlignCenter)
        thanks.setStyleSheet("color: #4CAF50; font-size: 12pt;")
        layout.addWidget(thanks)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(receipt.accept)
        layout.addWidget(close_btn)
        
        receipt.exec_()


class ProductSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.selected_product = None
        self.quantity = 1
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setWindowTitle("Search Products")
        self.setGeometry(300, 300, 600, 500)
        
        layout = QVBoxLayout(self)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or barcode...")
        self.search_input.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Barcode", "Product", "Price", "Stock"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.products_table)
        
        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 99)
        self.qty_spin.setValue(1)
        qty_layout.addWidget(self.qty_spin)
        qty_layout.addStretch()
        layout.addLayout(qty_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.accept)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_products(self):
        search = self.search_input.text()
        if search:
            # Fixed: Changed %s to ?
            query = "SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? LIMIT 20"
            search_term = f"%{search}%"
            products = self.db.fetch_all(query, (search_term, search_term))
        else:
            query = "SELECT * FROM products LIMIT 20"
            products = self.db.fetch_all(query)
        
        self.products_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product['barcode']))
            self.products_table.setItem(i, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(i, 2, QTableWidgetItem(format_currency(product['selling_price'])))
            
            stock_item = QTableWidgetItem(str(product['quantity']))
            if product['quantity'] <= product['reorder_level']:
                stock_item.setForeground(QColor('#F44336'))
            self.products_table.setItem(i, 3, stock_item)
    
    def select_product(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        # Fixed: Changed %s to ?
        query = "SELECT * FROM products WHERE barcode = ?"
        self.selected_product = self.db.fetch_one(query, (barcode,))
        self.quantity = self.qty_spin.value()
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product, self.quantity
