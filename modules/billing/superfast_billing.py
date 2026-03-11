from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QSpinBox, QDoubleSpinBox, QMessageBox, QDialog,
                           QFrame, QScrollArea, QComboBox, QShortcut)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor, QKeySequence
from database.connection import DatabaseConnection
from utils.helpers import format_currency, generate_invoice_number, calculate_tax
from datetime import datetime
import json

class SuperfastBillingModule(QWidget):
    billing_completed = pyqtSignal(dict)
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.cart_items = []
        self.current_customer = None
        self.barcode_buffer = ""
        self.barcode_timer = QTimer()
        self.barcode_timer.setSingleShot(True)
        self.barcode_timer.timeout.connect(self.process_barcode)
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_quick_products()
        
    def init_ui(self):
        # Main layout with three columns
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Quick products & customer
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # Center panel - Cart and billing
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 3)
        
        # Right panel - Payment and totals
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
    def create_left_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("⚡ Superfast Billing")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Barcode scanner section
        scanner_group = QGroupBox("Barcode Scanner")
        scanner_layout = QVBoxLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode or type here...")
        self.barcode_input.setFont(QFont("Arial", 14))
        self.barcode_input.setFixedHeight(50)
        self.barcode_input.textChanged.connect(self.on_barcode_input)
        self.barcode_input.returnPressed.connect(self.process_barcode)
        scanner_layout.addWidget(self.barcode_input)
        
        scanner_group.setLayout(scanner_layout)
        layout.addWidget(scanner_group)
        
        # Customer section
        customer_group = QGroupBox("Customer (Optional)")
        customer_layout = QVBoxLayout()
        
        customer_search_layout = QHBoxLayout()
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Search by phone or name...")
        self.customer_search.textChanged.connect(self.search_customers)
        customer_search_layout.addWidget(self.customer_search)
        
        self.new_customer_btn = QPushButton("➕ New")
        self.new_customer_btn.clicked.connect(self.show_new_customer_dialog)
        customer_search_layout.addWidget(self.new_customer_btn)
        
        customer_layout.addLayout(customer_search_layout)
        
        self.customer_list = QComboBox()
        self.customer_list.addItem("Walk-in Customer", None)
        self.customer_list.currentIndexChanged.connect(self.on_customer_selected)
        customer_layout.addWidget(self.customer_list)
        
        self.loyalty_points_label = QLabel("Loyalty Points: 0")
        self.loyalty_points_label.setStyleSheet("color: #FF9800;")
        customer_layout.addWidget(self.loyalty_points_label)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Quick products grid
        quick_group = QGroupBox("Quick Products")
        quick_layout = QGridLayout()
        
        self.quick_products = []
        self.create_quick_product_buttons(quick_layout)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # Recent items
        recent_group = QGroupBox("Recently Scanned")
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(2)
        self.recent_table.setHorizontalHeaderLabels(["Product", "Price"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_layout.addWidget(self.recent_table)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        return panel
    
    def create_center_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        
        layout = QVBoxLayout(panel)
        
        # Cart header
        header_layout = QHBoxLayout()
        
        cart_title = QLabel("🛒 Current Bill")
        cart_title.setFont(QFont("Arial", 16, QFont.Bold))
        cart_title.setStyleSheet("color: #2196F3;")
        header_layout.addWidget(cart_title)
        
        self.item_count_label = QLabel("0 items")
        self.item_count_label.setFont(QFont("Arial", 12))
        header_layout.addWidget(self.item_count_label)
        
        header_layout.addStretch()
        
        clear_cart_btn = QPushButton("🗑️ Clear All")
        clear_cart_btn.clicked.connect(self.clear_cart)
        clear_cart_btn.setStyleSheet("background-color: #F44336;")
        header_layout.addWidget(clear_cart_btn)
        
        layout.addLayout(header_layout)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["Product", "MRP", "Qty", "Discount %", "Total", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.verticalHeader().setVisible(False)
        layout.addWidget(self.cart_table)
        
        return panel
    
    def create_right_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("background-color: white; border-radius: 10px;")
        
        layout = QVBoxLayout(panel)
        
        # Bill summary
        summary_group = QGroupBox("Bill Summary")
        summary_layout = QGridLayout()
        
        summary_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("₹ 0.00")
        self.subtotal_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.subtotal_label, 0, 1)
        
        summary_layout.addWidget(QLabel("Discount:"), 1, 0)
        self.discount_label = QLabel("₹ 0.00")
        self.discount_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.discount_label, 1, 1)
        
        summary_layout.addWidget(QLabel("Tax (GST):"), 2, 0)
        self.tax_label = QLabel("₹ 0.00")
        self.tax_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.tax_label, 2, 1)
        
        # Total
        total_line = QFrame()
        total_line.setFrameShape(QFrame.HLine)
        total_line.setFrameShadow(QFrame.Sunken)
        summary_layout.addWidget(total_line, 3, 0, 1, 2)
        
        summary_layout.addWidget(QLabel("TOTAL:"), 4, 0)
        self.total_label = QLabel("₹ 0.00")
        self.total_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(self.total_label, 4, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Payment section
        payment_group = QGroupBox("Payment")
        payment_layout = QVBoxLayout()
        
        # Payment method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "UPI", "Mixed"])
        method_layout.addWidget(self.payment_method)
        payment_layout.addLayout(method_layout)
        
        # Cash given (for cash payment)
        cash_layout = QHBoxLayout()
        cash_layout.addWidget(QLabel("Cash Given:"))
        self.cash_given = QDoubleSpinBox()
        self.cash_given.setRange(0, 999999)
        self.cash_given.setPrefix("₹ ")
        self.cash_given.valueChanged.connect(self.calculate_change)
        cash_layout.addWidget(self.cash_given)
        payment_layout.addLayout(cash_layout)
        
        # Change
        change_layout = QHBoxLayout()
        change_layout.addWidget(QLabel("Change:"))
        self.change_label = QLabel("₹ 0.00")
        self.change_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.change_label.setStyleSheet("color: #4CAF50;")
        change_layout.addWidget(self.change_label)
        payment_layout.addLayout(change_layout)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Action buttons
        self.hold_bill_btn = QPushButton("⏸️ Hold Bill")
        self.hold_bill_btn.clicked.connect(self.hold_bill)
        layout.addWidget(self.hold_bill_btn)
        
        self.print_bill_btn = QPushButton("🖨️ Print Bill")
        self.print_bill_btn.clicked.connect(self.print_bill)
        layout.addWidget(self.print_bill_btn)
        
        self.payment_btn = QPushButton("💰 Complete Payment")
        self.payment_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.payment_btn.clicked.connect(self.complete_payment)
        layout.addWidget(self.payment_btn)
        
        layout.addStretch()
        
        return panel
    
    def create_quick_product_buttons(self, layout):
        # Create 8 quick product buttons (2 rows, 4 columns)
        products = [
            ("🥛 Milk", 60, "890123456001"),
            ("🍞 Bread", 40, "890123456002"),
            ("🥚 Eggs", 80, "890123456003"),
            ("🍚 Rice", 120, "890123456004"),
            ("🫘 Dal", 110, "890123456005"),
            ("🛢️ Oil", 130, "890123456006"),
            ("🧂 Sugar", 48, "890123456007"),
            ("🧋 Tea", 250, "890123456008")
        ]
        
        for i, (name, price, barcode) in enumerate(products):
            row = i // 4
            col = i % 4
            
            btn = QPushButton(f"{name}\n{format_currency(price)}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #2196F3;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, p=price, b=barcode: self.add_quick_product(n, p, b))
            layout.addWidget(btn, row, col)
    
    def setup_shortcuts(self):
        # Keyboard shortcuts for faster billing
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.new_bill)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_bill)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.hold_bill)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.complete_payment)
        QShortcut(QKeySequence("F1"), self).activated.connect(lambda: self.add_quick_product("Milk", 60, "890123456001"))
        QShortcut(QKeySequence("F2"), self).activated.connect(lambda: self.add_quick_product("Bread", 40, "890123456002"))
    
    def load_quick_products(self):
        # Load popular products for quick buttons
        query = """
            SELECT p.*, COUNT(si.id) as sale_count
            FROM products p
            LEFT JOIN sale_items si ON p.id = si.product_id
            GROUP BY p.id
            ORDER BY sale_count DESC
            LIMIT 8
        """
        products = self.db.fetch_all(query)
        
        # Update quick buttons if we have data
        if products:
            # This would update the buttons dynamically
            pass
    
    def on_barcode_input(self, text):
        # Accumulate barcode input
        self.barcode_buffer += text
        self.barcode_timer.start(100)  # Wait 100ms for more input
    
    def process_barcode(self):
        barcode = self.barcode_buffer.strip()
        self.barcode_buffer = ""
        self.barcode_input.clear()
        
        if barcode:
            self.scan_product(barcode)
    
    def scan_product(self, barcode):
        # Find product by barcode
        query = "SELECT * FROM products WHERE barcode = %s"
        product = self.db.fetch_one(query, (barcode,))
        
        if product:
            self.add_to_cart(product)
            self.add_to_recent(product)
        else:
            # Try to find by partial match or show dialog
            self.search_and_add_product(barcode)
    
    def search_and_add_product(self, search_term):
        dialog = QuickProductSearchDialog(search_term, self)
        if dialog.exec_():
            product = dialog.get_selected_product()
            if product:
                self.add_to_cart(product)
    
    def add_to_cart(self, product, quantity=1):
        # Check if product already in cart
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                item['quantity'] += quantity
                item['total'] = item['quantity'] * item['price'] * (1 - item['discount']/100)
                self.update_cart_display()
                self.calculate_totals()
                return
        
        # Add new item
        self.cart_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'barcode': product['barcode'],
            'price': float(product['selling_price']),
            'quantity': quantity,
            'discount': 0,
            'total': quantity * float(product['selling_price'])
        })
        
        self.update_cart_display()
        self.calculate_totals()
    
    def add_quick_product(self, name, price, barcode):
        # Create a pseudo product for quick add
        product = {
            'id': None,
            'name': name,
            'barcode': barcode,
            'selling_price': price
        }
        self.add_to_cart(product)
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart_items))
        
        for i, item in enumerate(self.cart_items):
            # Product name
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            
            # MRP
            price_item = QTableWidgetItem(format_currency(item['price']))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(i, 1, price_item)
            
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
            qty_label.setMinimumWidth(40)
            qty_layout.addWidget(qty_label)
            
            plus_btn = QPushButton("+")
            plus_btn.setMaximumWidth(30)
            plus_btn.clicked.connect(lambda checked, idx=i: self.adjust_quantity(idx, 1))
            qty_layout.addWidget(plus_btn)
            
            self.cart_table.setCellWidget(i, 2, qty_widget)
            
            # Discount
            discount_spin = QDoubleSpinBox()
            discount_spin.setRange(0, 100)
            discount_spin.setValue(item['discount'])
            discount_spin.setSuffix("%")
            discount_spin.valueChanged.connect(lambda value, idx=i: self.update_discount(idx, value))
            self.cart_table.setCellWidget(i, 3, discount_spin)
            
            # Total
            total_item = QTableWidgetItem(format_currency(item['total']))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.cart_table.setItem(i, 4, total_item)
            
            # Remove button
            remove_btn = QPushButton("✖")
            remove_btn.setMaximumWidth(30)
            remove_btn.setStyleSheet("background-color: #F44336; color: white;")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 5, remove_btn)
        
        self.item_count_label.setText(f"{len(self.cart_items)} items")
    
    def adjust_quantity(self, index, change):
        if 0 <= index < len(self.cart_items):
            new_qty = self.cart_items[index]['quantity'] + change
            if new_qty > 0:
                self.cart_items[index]['quantity'] = new_qty
                self.cart_items[index]['total'] = new_qty * self.cart_items[index]['price'] * (1 - self.cart_items[index]['discount']/100)
                self.update_cart_display()
                self.calculate_totals()
            elif new_qty == 0:
                self.remove_from_cart(index)
    
    def update_discount(self, index, discount):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['discount'] = discount
            self.cart_items[index]['total'] = self.cart_items[index]['quantity'] * self.cart_items[index]['price'] * (1 - discount/100)
            self.update_cart_display()
            self.calculate_totals()
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart_items):
            del self.cart_items[index]
            self.update_cart_display()
            self.calculate_totals()
    
    def calculate_totals(self):
        subtotal = sum(item['quantity'] * item['price'] for item in self.cart_items)
        discount = sum(item['quantity'] * item['price'] * item['discount']/100 for item in self.cart_items)
        taxable = subtotal - discount
        tax = taxable * 0.10  # 10% GST
        total = taxable + tax
        
        self.subtotal_label.setText(format_currency(subtotal))
        self.discount_label.setText(format_currency(discount))
        self.tax_label.setText(format_currency(tax))
        self.total_label.setText(format_currency(total))
        
        self.calculate_change()
        
        return total
    
    def calculate_change(self):
        total = float(self.total_label.text().replace('₹', '').replace(',', '').strip())
        cash = self.cash_given.value()
        
        if cash >= total:
            change = cash - total
            self.change_label.setText(format_currency(change))
        else:
            self.change_label.setText("Insufficient")
    
    def clear_cart(self):
        reply = QMessageBox.question(self, "Clear Cart", 
                                    "Clear all items from cart?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_display()
            self.calculate_totals()
    
    def new_bill(self):
        self.clear_cart()
        self.barcode_input.setFocus()
    
    def hold_bill(self):
        if not self.cart_items:
            return
        
        # Save current bill to temporary storage
        try:
            bill_data = {
                'items': self.cart_items,
                'customer': self.current_customer,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in database or file
            # For now, just show message
            QMessageBox.information(self, "Bill Held", 
                                  f"Bill with {len(self.cart_items)} items has been held.")
            
            self.clear_cart()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to hold bill: {str(e)}")
    
    def print_bill(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "No items to bill.")
            return
        
        # Generate receipt preview
        receipt = self.generate_receipt()
        
        # Show receipt dialog
        dialog = ReceiptDialog(receipt, self)
        dialog.exec_()
    
    def generate_receipt(self):
        receipt = []
        receipt.append("=" * 40)
        receipt.append("SUPERMARKET ERP")
        receipt.append("=" * 40)
        receipt.append(f"Bill No: {generate_invoice_number()}")
        receipt.append(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        receipt.append(f"Cashier: {self.user['full_name']}")
        receipt.append("-" * 40)
        
        for item in self.cart_items:
            receipt.append(f"{item['product_name'][:20]}")
            receipt.append(f"  {item['quantity']} x {format_currency(item['price'])} = {format_currency(item['total'])}")
        
        receipt.append("-" * 40)
        receipt.append(f"Subtotal: {self.subtotal_label.text()}")
        receipt.append(f"Discount: {self.discount_label.text()}")
        receipt.append(f"Tax: {self.tax_label.text()}")
        receipt.append("=" * 40)
        receipt.append(f"TOTAL: {self.total_label.text()}")
        receipt.append("=" * 40)
        receipt.append("Thank you for shopping!")
        receipt.append("Visit again!")
        
        return "\n".join(receipt)
    
    def complete_payment(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "No items to bill.")
            return
        
        total = self.calculate_totals()
        method = self.payment_method.currentText().lower()
        
        # Validate payment
        if method == 'cash':
            cash = self.cash_given.value()
            if cash < total:
                QMessageBox.warning(self, "Insufficient Payment", 
                                   f"Cash given ({format_currency(cash)}) is less than total ({format_currency(total)})")
                return
        
        try:
            # Create sale record
            invoice = generate_invoice_number()
            
            # Prepare sale items
            items = []
            for item in self.cart_items:
                items.append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'subtotal': item['total']
                })
            
            # Insert sale
            sale_query = """
                INSERT INTO sales (
                    invoice_number, user_id, customer_id, total_amount, 
                    discount, tax, payment_method, billing_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'quick')
            """
            
            customer_id = self.current_customer['id'] if self.current_customer else None
            
            cursor = self.db.execute_query(sale_query, (
                invoice,
                self.user['id'],
                customer_id,
                total,
                float(self.discount_label.text().replace('₹', '').replace(',', '').strip()),
                float(self.tax_label.text().replace('₹', '').replace(',', '').strip()),
                method
            ))
            
            if cursor:
                sale_id = cursor.lastrowid
                
                # Insert items
                for item in items:
                    item_query = """
                        INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    self.db.execute_query(item_query, (
                        sale_id,
                        item['product_id'],
                        item['quantity'],
                        item['price'],
                        item['subtotal']
                    ))
                    
                    # Update stock
                    stock_query = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
                    self.db.execute_query(stock_query, (item['quantity'], item['product_id']))
                
                # Update loyalty points if customer
                if customer_id:
                    points = int(total / 100)  # 1 point per ₹100
                    points_query = "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE id = %s"
                    self.db.execute_query(points_query, (points, customer_id))
                
                # Show success
                receipt = self.generate_receipt()
                QMessageBox.information(self, "Payment Successful", 
                                      f"Bill #{invoice}\n\n{receipt}")
                
                # Emit signal
                self.billing_completed.emit({
                    'invoice': invoice,
                    'total': total,
                    'items': len(self.cart_items)
                })
                
                # Clear cart for next customer
                self.clear_cart()
                self.barcode_input.setFocus()
                
        except Exception as e:
            QMessageBox.critical(self, "Payment Error", f"Failed to process payment: {str(e)}")
    
    def add_to_recent(self, product):
        # Add to recent table
        row = self.recent_table.rowCount()
        self.recent_table.insertRow(0)
        self.recent_table.setItem(0, 0, QTableWidgetItem(product['name']))
        self.recent_table.setItem(0, 1, QTableWidgetItem(format_currency(product['selling_price'])))
        
        # Keep only last 10 items
        if self.recent_table.rowCount() > 10:
            self.recent_table.removeRow(10)
    
    def search_customers(self, text):
        if len(text) < 3:
            return
        
        query = "SELECT id, name, phone, loyalty_points FROM customers WHERE phone LIKE %s OR name LIKE %s LIMIT 10"
        search_term = f"%{text}%"
        customers = self.db.fetch_all(query, (search_term, search_term))
        
        self.customer_list.clear()
        self.customer_list.addItem("Walk-in Customer", None)
        
        for customer in customers:
            display = f"{customer['name']} ({customer['phone']})"
            self.customer_list.addItem(display, customer['id'])
    
    def on_customer_selected(self, index):
        customer_id = self.customer_list.currentData()
        if customer_id:
            query = "SELECT * FROM customers WHERE id = %s"
            self.current_customer = self.db.fetch_one(query, (customer_id,))
            if self.current_customer:
                self.loyalty_points_label.setText(f"Loyalty Points: {self.current_customer['loyalty_points']}")
        else:
            self.current_customer = None
            self.loyalty_points_label.setText("Loyalty Points: 0")
    
    def show_new_customer_dialog(self):
        dialog = NewCustomerDialog(self)
        if dialog.exec_():
            customer = dialog.get_customer()
            self.customer_list.addItem(f"{customer['name']} ({customer['phone']})", customer['id'])
            self.customer_list.setCurrentIndex(self.customer_list.count() - 1)


class QuickProductSearchDialog(QDialog):
    def __init__(self, search_term, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.search_term = search_term
        self.selected_product = None
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setWindowTitle("Search Product")
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout(self)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setText(self.search_term)
        self.search_input.textChanged.connect(self.load_products)
        layout.addWidget(self.search_input)
        
        # Results
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Barcode", "Product", "Price"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.products_table)
        
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
        query = "SELECT * FROM products WHERE name LIKE %s OR barcode LIKE %s LIMIT 20"
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
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product


class NewCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.customer = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("New Customer")
        self.setGeometry(400, 300, 400, 300)
        
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
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Customer")
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
            query = """
                INSERT INTO customers (name, phone, email)
                VALUES (%s, %s, %s)
            """
            cursor = self.db.execute_query(query, (name, phone, self.email_input.text()))
            
            if cursor:
                self.customer = {
                    'id': cursor.lastrowid,
                    'name': name,
                    'phone': phone
                }
                QMessageBox.information(self, "Success", "Customer added successfully!")
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add customer: {str(e)}")
    
    def get_customer(self):
        return self.customer


class ReceiptDialog(QDialog):
    def __init__(self, receipt_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Receipt Preview")
        self.setGeometry(400, 300, 300, 500)
        
        layout = QVBoxLayout(self)
        
        # Receipt display
        receipt = QTextEdit()
        receipt.setFont(QFont("Courier New", 10))
        receipt.setText(receipt_text)
        receipt.setReadOnly(True)
        layout.addWidget(receipt)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Print")
        print_btn.clicked.connect(self.print_receipt)
        button_layout.addWidget(print_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def print_receipt(self):
        # Implement actual printing here
        QMessageBox.information(self, "Print", "Receipt sent to printer.")
        self.accept()
