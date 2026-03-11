from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QDateTimeEdit, QMessageBox, QDialog, QFormLayout,
                           QTabWidget, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import generate_invoice_number, format_currency
from datetime import datetime, timedelta

class OnlineOrderingModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_order = None
        self.init_ui()
        self.load_orders()
        
        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_orders)
        self.timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🛵 Online Ordering & Home Delivery")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Order List
        left_panel = self.create_order_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Order Details
        right_panel = self.create_order_details_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.new_order_btn = QPushButton("➕ New Order")
        self.new_order_btn.clicked.connect(self.show_new_order_dialog)
        buttons_layout.addWidget(self.new_order_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_orders)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.delivery_btn = QPushButton("🚚 Assign Delivery")
        self.delivery_btn.clicked.connect(self.assign_delivery)
        buttons_layout.addWidget(self.delivery_btn)
        
        self.update_status_btn = QPushButton("📦 Update Status")
        self.update_status_btn.clicked.connect(self.update_order_status)
        buttons_layout.addWidget(self.update_status_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def create_order_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'pending', 'confirmed', 'preparing', 
                                    'out_for_delivery', 'delivered', 'cancelled'])
        self.status_filter.currentTextChanged.connect(self.load_orders)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by order # or customer...")
        self.search_box.textChanged.connect(self.load_orders)
        filter_layout.addWidget(self.search_box)
        
        layout.addLayout(filter_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order #", "Customer", "Amount", "Status", "Payment", 
            "Delivery", "Order Time", "Actions"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.itemClicked.connect(self.on_order_selected)
        layout.addWidget(self.orders_table)
        
        return panel
    
    def create_order_details_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Order info group
        info_group = QGroupBox("Order Information")
        info_layout = QGridLayout()
        
        self.order_number_label = QLabel("Order #: -")
        info_layout.addWidget(QLabel("Order Number:"), 0, 0)
        info_layout.addWidget(self.order_number_label, 0, 1)
        
        self.customer_label = QLabel("-")
        info_layout.addWidget(QLabel("Customer:"), 1, 0)
        info_layout.addWidget(self.customer_label, 1, 1)
        
        self.phone_label = QLabel("-")
        info_layout.addWidget(QLabel("Phone:"), 2, 0)
        info_layout.addWidget(self.phone_label, 2, 1)
        
        self.address_label = QLabel("-")
        info_layout.addWidget(QLabel("Address:"), 3, 0)
        info_layout.addWidget(self.address_label, 3, 1)
        
        self.delivery_label = QLabel("-")
        info_layout.addWidget(QLabel("Delivery Date:"), 4, 0)
        info_layout.addWidget(self.delivery_label, 4, 1)
        
        self.status_label = QLabel("-")
        info_layout.addWidget(QLabel("Status:"), 5, 0)
        info_layout.addWidget(self.status_label, 5, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Items table
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Subtotal"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Summary
        summary_group = QGroupBox("Order Summary")
        summary_layout = QGridLayout()
        
        self.subtotal_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        summary_layout.addWidget(self.subtotal_label, 0, 1)
        
        self.delivery_charge_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Delivery Charge:"), 1, 0)
        summary_layout.addWidget(self.delivery_charge_label, 1, 1)
        
        self.discount_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Discount:"), 2, 0)
        summary_layout.addWidget(self.discount_label, 2, 1)
        
        self.tax_label = QLabel("₹ 0.00")
        summary_layout.addWidget(QLabel("Tax:"), 3, 0)
        summary_layout.addWidget(self.tax_label, 3, 1)
        
        self.total_label = QLabel("₹ 0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(QLabel("Total:"), 4, 0)
        summary_layout.addWidget(self.total_label, 4, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        return panel
    
    def load_orders(self):
        try:
            status = self.status_filter.currentText()
            search = self.search_box.text()
            
            query = """
                SELECT o.*, c.name as customer_name 
                FROM online_orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                WHERE 1=1
            """
            params = []
            
            if status != 'All':
                query += " AND o.delivery_status = %s"
                params.append(status)
            
            if search:
                query += " AND (o.order_number LIKE %s OR c.name LIKE %s OR o.customer_phone LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            query += " ORDER BY o.created_at DESC"
            
            orders = self.db.fetch_all(query, params)
            
            self.orders_table.setRowCount(len(orders))
            for i, order in enumerate(orders):
                self.orders_table.setItem(i, 0, QTableWidgetItem(order['order_number']))
                self.orders_table.setItem(i, 1, QTableWidgetItem(order.get('customer_name', order['customer_name'])))
                self.orders_table.setItem(i, 2, QTableWidgetItem(format_currency(order['total_amount'])))
                
                # Status with color
                status_item = QTableWidgetItem(order['delivery_status'])
                if order['delivery_status'] == 'delivered':
                    status_item.setForeground(QColor('#4CAF50'))
                elif order['delivery_status'] == 'cancelled':
                    status_item.setForeground(QColor('#F44336'))
                elif order['delivery_status'] == 'out_for_delivery':
                    status_item.setForeground(QColor('#FF9800'))
                self.orders_table.setItem(i, 3, status_item)
                
                self.orders_table.setItem(i, 4, QTableWidgetItem(order['payment_status']))
                self.orders_table.setItem(i, 5, QTableWidgetItem(order.get('assigned_delivery_person', 'Unassigned')))
                self.orders_table.setItem(i, 6, QTableWidgetItem(order['created_at'].strftime('%H:%M %d/%m')))
                
                # View button
                view_btn = QPushButton("👁️ View")
                view_btn.clicked.connect(lambda checked, o=order: self.view_order(o))
                self.orders_table.setCellWidget(i, 7, view_btn)
                
        except Exception as e:
            print(f"Error loading orders: {e}")
    
    def on_order_selected(self, item):
        row = item.row()
        order_number = self.orders_table.item(row, 0).text()
        self.load_order_details(order_number)
    
    def load_order_details(self, order_number):
        try:
            # Load order header
            query = """
                SELECT o.*, c.name as customer_name 
                FROM online_orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                WHERE o.order_number = %s
            """
            order = self.db.fetch_one(query, (order_number,))
            
            if order:
                self.current_order = order
                self.order_number_label.setText(f"Order #: {order['order_number']}")
                self.customer_label.setText(order.get('customer_name', order['customer_name']))
                self.phone_label.setText(order['customer_phone'])
                self.address_label.setText(order['delivery_address'] or order['customer_address'])
                
                if order['delivery_date']:
                    self.delivery_label.setText(order['delivery_date'].strftime('%d/%m/%Y %H:%M'))
                else:
                    self.delivery_label.setText("Not scheduled")
                
                # Status with color
                status_text = order['delivery_status'].replace('_', ' ').title()
                self.status_label.setText(status_text)
                
                # Load order items
                items_query = """
                    SELECT oi.*, p.name as product_name
                    FROM online_order_items oi
                    LEFT JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                """
                items = self.db.fetch_all(items_query, (order['id'],))
                
                self.items_table.setRowCount(len(items))
                subtotal = 0
                for i, item in enumerate(items):
                    self.items_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
                    self.items_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
                    self.items_table.setItem(i, 2, QTableWidgetItem(format_currency(item['price'])))
                    self.items_table.setItem(i, 3, QTableWidgetItem(format_currency(item['subtotal'])))
                    subtotal += item['subtotal']
                
                # Update summary
                self.subtotal_label.setText(format_currency(subtotal))
                self.delivery_charge_label.setText(format_currency(order['delivery_charge']))
                self.discount_label.setText(format_currency(order['discount']))
                self.tax_label.setText(format_currency(order['tax']))
                self.total_label.setText(format_currency(order['total_amount']))
                
                self.notes_text.setText(order['order_notes'] or 'No notes')
                
        except Exception as e:
            print(f"Error loading order details: {e}")
    
    def show_new_order_dialog(self):
        dialog = NewOrderDialog(self.user, self)
        if dialog.exec_():
            self.load_orders()
    
    def assign_delivery(self):
        if not self.current_order:
            QMessageBox.warning(self, "No Order", "Please select an order first.")
            return
        
        dialog = AssignDeliveryDialog(self.current_order, self)
        if dialog.exec_():
            self.load_order_details(self.current_order['order_number'])
            self.load_orders()
    
    def update_order_status(self):
        if not self.current_order:
            QMessageBox.warning(self, "No Order", "Please select an order first.")
            return
        
        dialog = UpdateStatusDialog(self.current_order, self)
        if dialog.exec_():
            self.load_order_details(self.current_order['order_number'])
            self.load_orders()
    
    def view_order(self, order):
        self.load_order_details(order['order_number'])


class NewOrderDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.db = DatabaseConnection()
        self.cart_items = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("New Online Order")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Customer details
        customer_group = QGroupBox("Customer Details")
        customer_layout = QGridLayout()
        
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        customer_layout.addWidget(QLabel("Name:*"), 0, 0)
        customer_layout.addWidget(self.customer_name, 0, 1)
        
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone Number")
        customer_layout.addWidget(QLabel("Phone:*"), 1, 0)
        customer_layout.addWidget(self.customer_phone, 1, 1)
        
        self.customer_address = QTextEdit()
        self.customer_address.setPlaceholderText("Delivery Address")
        self.customer_address.setMaximumHeight(80)
        customer_layout.addWidget(QLabel("Address:*"), 2, 0)
        customer_layout.addWidget(self.customer_address, 2, 1)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Order items
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        
        # Product search
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search products by name or barcode...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        
        self.add_product_btn = QPushButton("➕ Add to Cart")
        self.add_product_btn.clicked.connect(self.show_product_dialog)
        search_layout.addWidget(self.add_product_btn)
        
        items_layout.addLayout(search_layout)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Subtotal", "Action"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.cart_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Delivery options
        delivery_group = QGroupBox("Delivery Options")
        delivery_layout = QGridLayout()
        
        self.delivery_date = QDateTimeEdit()
        self.delivery_date.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.delivery_date.setCalendarPopup(True)
        delivery_layout.addWidget(QLabel("Delivery Date:"), 0, 0)
        delivery_layout.addWidget(self.delivery_date, 0, 1)
        
        self.delivery_charge = QDoubleSpinBox()
        self.delivery_charge.setRange(0, 1000)
        self.delivery_charge.setValue(50)
        self.delivery_charge.valueChanged.connect(self.calculate_total)
        delivery_layout.addWidget(QLabel("Delivery Charge:"), 1, 0)
        delivery_layout.addWidget(self.delivery_charge, 1, 1)
        
        self.discount = QDoubleSpinBox()
        self.discount.setRange(0, 10000)
        self.discount.valueChanged.connect(self.calculate_total)
        delivery_layout.addWidget(QLabel("Discount:"), 2, 0)
        delivery_layout.addWidget(self.discount, 2, 1)
        
        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)
        
        # Summary
        summary_layout = QHBoxLayout()
        
        self.subtotal_label = QLabel("Subtotal: ₹ 0.00")
        self.subtotal_label.setFont(QFont("Arial", 10))
        summary_layout.addWidget(self.subtotal_label)
        
        self.total_label = QLabel("Total: ₹ 0.00")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(self.total_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Create Order")
        self.save_btn.clicked.connect(self.save_order)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def search_products(self):
        # Implement product search
        pass
    
    def show_product_dialog(self):
        dialog = ProductSearchDialog(self)
        if dialog.exec_():
            product, quantity = dialog.get_selected_product()
            if product:
                self.add_to_cart(product, quantity)
    
    def add_to_cart(self, product, quantity):
        # Check if product already in cart
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                item['quantity'] += quantity
                item['subtotal'] = item['quantity'] * item['price']
                self.update_cart_table()
                self.calculate_total()
                return
        
        # Add new item
        self.cart_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'quantity': quantity,
            'price': float(product['selling_price']),
            'subtotal': quantity * float(product['selling_price'])
        })
        self.update_cart_table()
        self.calculate_total()
    
    def update_cart_table(self):
        self.cart_table.setRowCount(len(self.cart_items))
        for i, item in enumerate(self.cart_items):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            self.cart_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(i, 2, QTableWidgetItem(format_currency(item['price'])))
            self.cart_table.setItem(i, 3, QTableWidgetItem(format_currency(item['subtotal'])))
            
            remove_btn = QPushButton("❌")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
    
    def remove_from_cart(self, index):
        del self.cart_items[index]
        self.update_cart_table()
        self.calculate_total()
    
    def calculate_total(self):
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        self.subtotal_label.setText(f"Subtotal: {format_currency(subtotal)}")
        
        total = subtotal + self.delivery_charge.value() - self.discount.value()
        self.total_label.setText(f"Total: {format_currency(total)}")
    
    def save_order(self):
        if not self.customer_name.text() or not self.customer_phone.text() or not self.customer_address.toPlainText():
            QMessageBox.warning(self, "Validation Error", "Please fill all customer details.")
            return
        
        if not self.cart_items:
            QMessageBox.warning(self, "Validation Error", "Please add items to the order.")
            return
        
        try:
            order_number = generate_invoice_number().replace('INV', 'ORD')
            subtotal = sum(item['subtotal'] for item in self.cart_items)
            total = subtotal + self.delivery_charge.value() - self.discount.value()
            
            # Insert order
            order_query = """
                INSERT INTO online_orders (
                    order_number, customer_name, customer_phone, customer_address,
                    delivery_address, delivery_date, delivery_status, payment_status,
                    total_amount, delivery_charge, discount, tax, order_notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor = self.db.execute_query(order_query, (
                order_number,
                self.customer_name.text(),
                self.customer_phone.text(),
                self.customer_address.toPlainText(),
                self.customer_address.toPlainText(),  # Same as customer address for now
                self.delivery_date.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
                'pending',
                'pending',
                total,
                self.delivery_charge.value(),
                self.discount.value(),
                0,  # tax
                ''  # notes
            ))
            
            if cursor:
                order_id = cursor.lastrowid
                
                # Insert items
                for item in self.cart_items:
                    item_query = """
                        INSERT INTO online_order_items (order_id, product_id, quantity, price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    self.db.execute_query(item_query, (
                        order_id,
                        item['product_id'],
                        item['quantity'],
                        item['price'],
                        item['subtotal']
                    ))
                
                QMessageBox.information(self, "Success", f"Order {order_number} created successfully!")
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create order: {str(e)}")


class ProductSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.selected_product = None
        self.quantity = 1
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setWindowTitle("Select Product")
        self.setGeometry(300, 300, 600, 400)
        
        layout = QVBoxLayout(self)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search products...")
        self.search_box.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Barcode", "Product Name", "Price"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.products_table)
        
        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 999)
        self.qty_spin.setValue(1)
        qty_layout.addWidget(self.qty_spin)
        qty_layout.addStretch()
        layout.addLayout(qty_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Select")
        self.select_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.select_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_products(self):
        search = self.search_box.text()
        query = "SELECT * FROM products WHERE name LIKE %s OR barcode LIKE %s LIMIT 50"
        search_term = f"%{search}%"
        products = self.db.fetch_all(query, (search_term, search_term))
        
        self.products_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product['barcode']))
            self.products_table.setItem(i, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(i, 2, QTableWidgetItem(format_currency(product['selling_price'])))
    
    def select_product(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        query = "SELECT * FROM products WHERE barcode = %s"
        self.selected_product = self.db.fetch_one(query, (barcode,))
        self.quantity = self.qty_spin.value()
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product, self.quantity


class AssignDeliveryDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Assign Delivery Person")
        self.setGeometry(400, 300, 400, 200)
        
        layout = QVBoxLayout(self)
        
        # Order info
        info_label = QLabel(f"Order: {self.order['order_number']}")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(info_label)
        
        # Delivery person
        form_layout = QFormLayout()
        
        self.delivery_person = QLineEdit()
        self.delivery_person.setPlaceholderText("Enter delivery person name")
        form_layout.addRow("Delivery Person:", self.delivery_person)
        
        self.expected_time = QDateTimeEdit()
        self.expected_time.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.expected_time.setCalendarPopup(True)
        form_layout.addRow("Expected Delivery:", self.expected_time)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        assign_btn = QPushButton("✅ Assign")
        assign_btn.clicked.connect(self.assign)
        button_layout.addWidget(assign_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def assign(self):
        if not self.delivery_person.text():
            QMessageBox.warning(self, "Validation", "Please enter delivery person name.")
            return
        
        try:
            query = """
                UPDATE online_orders 
                SET assigned_delivery_person = %s, 
                    delivery_date = %s,
                    delivery_status = 'out_for_delivery'
                WHERE id = %s
            """
            self.db.execute_query(query, (
                self.delivery_person.text(),
                self.expected_time.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
                self.order['id']
            ))
            
            QMessageBox.information(self, "Success", "Delivery person assigned successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class UpdateStatusDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Update Order Status")
        self.setGeometry(400, 300, 300, 150)
        
        layout = QVBoxLayout(self)
        
        # Status selection
        layout.addWidget(QLabel(f"Order: {self.order['order_number']}"))
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'])
        layout.addWidget(self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        update_btn = QPushButton("✅ Update")
        update_btn.clicked.connect(self.update_status)
        button_layout.addWidget(update_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def update_status(self):
        try:
            query = "UPDATE online_orders SET delivery_status = %s WHERE id = %s"
            self.db.execute_query(query, (self.status_combo.currentText(), self.order['id']))
            
            QMessageBox.information(self, "Success", "Status updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
