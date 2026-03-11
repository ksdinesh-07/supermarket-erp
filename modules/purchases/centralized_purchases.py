from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QDateEdit, QMessageBox, QDialog, QTabWidget,
                           QSplitter, QFrame)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, generate_invoice_number
from datetime import datetime, timedelta

class CentralizedPurchasesModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_po = None
        self.po_items = []
        self.init_ui()
        self.load_purchase_orders()
        self.load_suppliers()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 Centralized Purchase Management")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Purchase Orders List
        left_panel = self.create_po_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - PO Form
        right_panel = self.create_po_form_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.new_po_btn = QPushButton("➕ New Purchase Order")
        self.new_po_btn.clicked.connect(self.new_purchase_order)
        buttons_layout.addWidget(self.new_po_btn)
        
        self.save_po_btn = QPushButton("💾 Save PO")
        self.save_po_btn.clicked.connect(self.save_purchase_order)
        self.save_po_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_po_btn)
        
        self.send_po_btn = QPushButton("📧 Send to Supplier")
        self.send_po_btn.clicked.connect(self.send_to_supplier)
        self.send_po_btn.setEnabled(False)
        buttons_layout.addWidget(self.send_po_btn)
        
        self.receive_po_btn = QPushButton("📦 Receive Order")
        self.receive_po_btn.clicked.connect(self.receive_order)
        self.receive_po_btn.setEnabled(False)
        buttons_layout.addWidget(self.receive_po_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_purchase_orders)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def create_po_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'draft', 'sent', 'confirmed', 'partial', 'received', 'cancelled'])
        self.status_filter.currentTextChanged.connect(self.load_purchase_orders)
        filter_layout.addWidget(self.status_filter, 0, 1)
        
        filter_layout.addWidget(QLabel("Supplier:"), 0, 2)
        self.supplier_filter = QComboBox()
        self.supplier_filter.addItem("All Suppliers")
        self.supplier_filter.currentTextChanged.connect(self.load_purchase_orders)
        filter_layout.addWidget(self.supplier_filter, 0, 3)
        
        filter_layout.addWidget(QLabel("Date From:"), 1, 0)
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.dateChanged.connect(self.load_purchase_orders)
        filter_layout.addWidget(self.date_from, 1, 1)
        
        filter_layout.addWidget(QLabel("Date To:"), 1, 2)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.dateChanged.connect(self.load_purchase_orders)
        filter_layout.addWidget(self.date_to, 1, 3)
        
        filter_layout.addWidget(QLabel("Search:"), 2, 0)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by PO # or supplier...")
        self.search_box.textChanged.connect(self.load_purchase_orders)
        filter_layout.addWidget(self.search_box, 2, 1, 1, 3)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Purchase Orders table
        self.po_table = QTableWidget()
        self.po_table.setColumnCount(8)
        self.po_table.setHorizontalHeaderLabels([
            "PO #", "Supplier", "Order Date", "Expected", "Items", "Amount", "Status", "Actions"
        ])
        self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.po_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.po_table.itemClicked.connect(self.on_po_selected)
        layout.addWidget(self.po_table)
        
        return panel
    
    def create_po_form_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # PO Header
        header_group = QGroupBox("Purchase Order Details")
        header_layout = QGridLayout()
        
        # Row 1
        header_layout.addWidget(QLabel("PO Number:"), 0, 0)
        self.po_number_label = QLabel("-")
        self.po_number_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(self.po_number_label, 0, 1)
        
        header_layout.addWidget(QLabel("Status:"), 0, 2)
        self.po_status_label = QLabel("Draft")
        self.po_status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
        header_layout.addWidget(self.po_status_label, 0, 3)
        
        # Row 2 - Supplier
        header_layout.addWidget(QLabel("Supplier:*"), 1, 0)
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        self.supplier_combo.currentIndexChanged.connect(self.on_supplier_selected)
        header_layout.addWidget(self.supplier_combo, 1, 1, 1, 3)
        
        # Row 3 - Dates
        header_layout.addWidget(QLabel("Order Date:"), 2, 0)
        self.order_date = QDateEdit()
        self.order_date.setDate(QDate.currentDate())
        self.order_date.setCalendarPopup(True)
        header_layout.addWidget(self.order_date, 2, 1)
        
        header_layout.addWidget(QLabel("Expected Delivery:"), 2, 2)
        self.expected_date = QDateEdit()
        self.expected_date.setDate(QDate.currentDate().addDays(7))
        self.expected_date.setCalendarPopup(True)
        header_layout.addWidget(self.expected_date, 2, 3)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items section
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        
        # Add item controls
        add_item_layout = QHBoxLayout()
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search product to add...")
        add_item_layout.addWidget(self.product_search)
        
        self.add_item_btn = QPushButton("➕ Add Item")
        self.add_item_btn.clicked.connect(self.show_product_dialog)
        add_item_layout.addWidget(self.add_item_btn)
        
        items_layout.addLayout(add_item_layout)
        
        # Items table
        self.po_items_table = QTableWidget()
        self.po_items_table.setColumnCount(6)
        self.po_items_table.setHorizontalHeaderLabels([
            "Product", "Quantity", "Unit Cost", "Total", "Status", "Action"
        ])
        self.po_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.po_items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Summary
        summary_group = QGroupBox("Order Summary")
        summary_layout = QGridLayout()
        
        summary_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("₹ 0.00")
        summary_layout.addWidget(self.subtotal_label, 0, 1)
        
        summary_layout.addWidget(QLabel("Discount:"), 0, 2)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100000)
        self.discount_input.setPrefix("₹ ")
        self.discount_input.valueChanged.connect(self.calculate_total)
        summary_layout.addWidget(self.discount_input, 0, 3)
        
        summary_layout.addWidget(QLabel("Tax:"), 1, 0)
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setRange(0, 100)
        self.tax_input.setSuffix("%")
        self.tax_input.setValue(18)
        self.tax_input.valueChanged.connect(self.calculate_total)
        summary_layout.addWidget(self.tax_input, 1, 1)
        
        summary_layout.addWidget(QLabel("Grand Total:"), 1, 2)
        self.grand_total_label = QLabel("₹ 0.00")
        self.grand_total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.grand_total_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(self.grand_total_label, 1, 3)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        self.po_notes = QTextEdit()
        self.po_notes.setMaximumHeight(80)
        notes_layout.addWidget(self.po_notes)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        return panel
    
    def load_suppliers(self):
        try:
            query = "SELECT * FROM suppliers WHERE status = 'active' ORDER BY name"
            suppliers = self.db.fetch_all(query)
            
            self.supplier_combo.clear()
            self.supplier_filter.clear()
            self.supplier_filter.addItem("All Suppliers")
            
            for supplier in suppliers:
                display_text = f"{supplier['name']} ({supplier['supplier_code']})"
                self.supplier_combo.addItem(display_text, supplier['id'])
                self.supplier_filter.addItem(display_text, supplier['id'])
                
        except Exception as e:
            print(f"Error loading suppliers: {e}")
    
    def load_purchase_orders(self):
        try:
            status = self.status_filter.currentText()
            supplier_id = self.supplier_filter.currentData()
            date_from = self.date_from.date().toString('yyyy-MM-dd')
            date_to = self.date_to.date().toString('yyyy-MM-dd')
            search = self.search_box.text()
            
            query = """
                SELECT po.*, s.name as supplier_name
                FROM purchase_orders po
                LEFT JOIN suppliers s ON po.supplier_id = s.id
                WHERE po.order_date BETWEEN %s AND %s
            """
            params = [date_from, date_to]
            
            if status != 'All':
                query += " AND po.status = %s"
                params.append(status.lower())
            
            if supplier_id:
                query += " AND po.supplier_id = %s"
                params.append(supplier_id)
            
            if search:
                query += " AND (po.po_number LIKE %s OR s.name LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            query += " ORDER BY po.created_at DESC"
            
            orders = self.db.fetch_all(query, params)
            
            self.po_table.setRowCount(len(orders))
            for i, order in enumerate(orders):
                self.po_table.setItem(i, 0, QTableWidgetItem(order['po_number']))
                self.po_table.setItem(i, 1, QTableWidgetItem(order.get('supplier_name', '-')))
                self.po_table.setItem(i, 2, QTableWidgetItem(str(order['order_date'])))
                self.po_table.setItem(i, 3, QTableWidgetItem(str(order['expected_delivery'] or '-')))
                self.po_table.setItem(i, 4, QTableWidgetItem(str(order['total_items'])))
                self.po_table.setItem(i, 5, QTableWidgetItem(format_currency(order['grand_total'])))
                
                status_item = QTableWidgetItem(order['status'].title())
                if order['status'] == 'received':
                    status_item.setForeground(QColor('#4CAF50'))
                elif order['status'] == 'sent':
                    status_item.setForeground(QColor('#2196F3'))
                elif order['status'] == 'confirmed':
                    status_item.setForeground(QColor('#FF9800'))
                elif order['status'] == 'cancelled':
                    status_item.setForeground(QColor('#F44336'))
                self.po_table.setItem(i, 6, status_item)
                
                view_btn = QPushButton("👁️ View")
                view_btn.clicked.connect(lambda checked, o=order: self.view_po(o))
                self.po_table.setCellWidget(i, 7, view_btn)
                
        except Exception as e:
            print(f"Error loading POs: {e}")
    
    def on_po_selected(self, item):
        row = item.row()
        po_number = self.po_table.item(row, 0).text()
        self.load_po_details(po_number)
    
    def load_po_details(self, po_number):
        try:
            query = "SELECT * FROM purchase_orders WHERE po_number = %s"
            po = self.db.fetch_one(query, (po_number,))
            
            if po:
                self.current_po = po
                self.po_number_label.setText(po['po_number'])
                
                # Set status
                status_text = po['status'].title()
                self.po_status_label.setText(status_text)
                
                if po['status'] == 'received':
                    self.po_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                elif po['status'] == 'sent':
                    self.po_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
                elif po['status'] == 'confirmed':
                    self.po_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                elif po['status'] == 'draft':
                    self.po_status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
                
                # Set supplier
                if po['supplier_id']:
                    index = self.supplier_combo.findData(po['supplier_id'])
                    if index >= 0:
                        self.supplier_combo.setCurrentIndex(index)
                
                # Set dates
                if po['order_date']:
                    self.order_date.setDate(QDate.fromString(str(po['order_date']), 'yyyy-MM-dd'))
                if po['expected_delivery']:
                    self.expected_date.setDate(QDate.fromString(str(po['expected_delivery']), 'yyyy-MM-dd'))
                
                # Set financials
                self.discount_input.setValue(float(po['discount'] or 0))
                self.tax_input.setValue(float(po['tax'] or 0))
                self.po_notes.setText(po['notes'] or '')
                
                # Load items
                items_query = """
                    SELECT poi.*, p.name as product_name
                    FROM purchase_order_items poi
                    LEFT JOIN products p ON poi.product_id = p.id
                    WHERE poi.po_id = %s
                """
                items = self.db.fetch_all(items_query, (po['id'],))
                
                self.po_items = []
                for item in items:
                    self.po_items.append({
                        'id': item['id'],
                        'product_id': item['product_id'],
                        'product_name': item['product_name'],
                        'quantity': item['quantity'],
                        'unit_cost': float(item['unit_cost']),
                        'total_cost': float(item['total_cost']),
                        'received_quantity': item['received_quantity'],
                        'status': item['status']
                    })
                
                self.update_po_items_table()
                self.calculate_total()
                
                # Enable/disable buttons
                if po['status'] == 'draft':
                    self.save_po_btn.setEnabled(True)
                    self.send_po_btn.setEnabled(True)
                    self.receive_po_btn.setEnabled(False)
                elif po['status'] in ['sent', 'confirmed', 'partial']:
                    self.save_po_btn.setEnabled(False)
                    self.send_po_btn.setEnabled(False)
                    self.receive_po_btn.setEnabled(True)
                else:
                    self.save_po_btn.setEnabled(False)
                    self.send_po_btn.setEnabled(False)
                    self.receive_po_btn.setEnabled(False)
                    
        except Exception as e:
            print(f"Error loading PO details: {e}")
    
    def new_purchase_order(self):
        self.current_po = None
        self.po_items = []
        
        po_number = f"PO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.po_number_label.setText(po_number)
        self.po_status_label.setText("Draft")
        self.po_status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
        
        self.order_date.setDate(QDate.currentDate())
        self.expected_date.setDate(QDate.currentDate().addDays(7))
        self.discount_input.setValue(0)
        self.tax_input.setValue(18)
        self.po_notes.clear()
        
        self.update_po_items_table()
        self.calculate_total()
        
        self.save_po_btn.setEnabled(True)
        self.send_po_btn.setEnabled(False)
        self.receive_po_btn.setEnabled(False)
    
    def on_supplier_selected(self, index):
        # Could load supplier details, payment terms, etc.
        pass
    
    def show_product_dialog(self):
        dialog = PurchaseProductDialog(self)
        if dialog.exec_():
            product, quantity = dialog.get_selected_product()
            if product:
                self.add_to_po(product, quantity)
    
    def add_to_po(self, product, quantity):
        # Check if product already in PO
        for item in self.po_items:
            if item['product_id'] == product['id']:
                # Update existing item
                item['quantity'] += quantity
                item['total_cost'] = item['quantity'] * item['unit_cost']
                self.update_po_items_table()
                self.calculate_total()
                return
        
        # Add new item
        self.po_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'quantity': quantity,
            'unit_cost': float(product['cost_price'] or 0),
            'total_cost': quantity * float(product['cost_price'] or 0),
            'received_quantity': 0,
            'status': 'pending'
        })
        
        self.update_po_items_table()
        self.calculate_total()
    
    def update_po_items_table(self):
        self.po_items_table.setRowCount(len(self.po_items))
        for i, item in enumerate(self.po_items):
            self.po_items_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            
            # Quantity with spin box
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            
            qty_spin = QSpinBox()
            qty_spin.setRange(1, 9999)
            qty_spin.setValue(item['quantity'])
            qty_spin.valueChanged.connect(lambda value, idx=i: self.update_item_quantity(idx, value))
            qty_layout.addWidget(qty_spin)
            
            self.po_items_table.setCellWidget(i, 1, qty_widget)
            
            # Unit cost
            cost_spin = QDoubleSpinBox()
            cost_spin.setRange(0, 999999)
            cost_spin.setValue(item['unit_cost'])
            cost_spin.setPrefix("₹ ")
            cost_spin.valueChanged.connect(lambda value, idx=i: self.update_item_cost(idx, value))
            self.po_items_table.setCellWidget(i, 2, cost_spin)
            
            # Total
            self.po_items_table.setItem(i, 3, QTableWidgetItem(format_currency(item['total_cost'])))
            
            # Status
            status_text = "Pending"
            if item['received_quantity'] >= item['quantity']:
                status_text = "Received"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor('#4CAF50'))
            elif item['received_quantity'] > 0:
                status_text = f"Partial ({item['received_quantity']}/{item['quantity']})"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor('#FF9800'))
            else:
                status_item = QTableWidgetItem(status_text)
            
            self.po_items_table.setItem(i, 4, status_item)
            
            # Remove button
            remove_btn = QPushButton("❌")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_po_item(idx))
            self.po_items_table.setCellWidget(i, 5, remove_btn)
    
    def update_item_quantity(self, index, quantity):
        if 0 <= index < len(self.po_items):
            self.po_items[index]['quantity'] = quantity
            self.po_items[index]['total_cost'] = quantity * self.po_items[index]['unit_cost']
            self.update_po_items_table()
            self.calculate_total()
    
    def update_item_cost(self, index, cost):
        if 0 <= index < len(self.po_items):
            self.po_items[index]['unit_cost'] = cost
            self.po_items[index]['total_cost'] = self.po_items[index]['quantity'] * cost
            self.update_po_items_table()
            self.calculate_total()
    
    def remove_po_item(self, index):
        if 0 <= index < len(self.po_items):
            del self.po_items[index]
            self.update_po_items_table()
            self.calculate_total()
    
    def calculate_total(self):
        subtotal = sum(item['total_cost'] for item in self.po_items)
        discount = self.discount_input.value()
        tax_rate = self.tax_input.value() / 100
        tax = (subtotal - discount) * tax_rate
        grand_total = subtotal - discount + tax
        
        self.subtotal_label.setText(format_currency(subtotal))
        self.grand_total_label.setText(format_currency(grand_total))
        
        return grand_total
    
    def save_purchase_order(self):
        if not self.validate_po_form():
            return
        
        try:
            grand_total = self.calculate_total()
            
            if self.current_po:
                # Update existing PO
                query = """
                    UPDATE purchase_orders 
                    SET supplier_id = %s, order_date = %s, expected_delivery = %s,
                        total_items = %s, total_amount = %s, discount = %s,
                        tax = %s, grand_total = %s, notes = %s
                    WHERE id = %s
                """
                self.db.execute_query(query, (
                    self.supplier_combo.currentData(),
                    self.order_date.date().toString('yyyy-MM-dd'),
                    self.expected_date.date().toString('yyyy-MM-dd'),
                    len(self.po_items),
                    sum(item['total_cost'] for item in self.po_items),
                    self.discount_input.value(),
                    self.tax_input.value(),
                    grand_total,
                    self.po_notes.toPlainText(),
                    self.current_po['id']
                ))
                
                # Delete old items
                del_query = "DELETE FROM purchase_order_items WHERE po_id = %s"
                self.db.execute_query(del_query, (self.current_po['id'],))
                
            else:
                # Check if PO number exists
                check_query = "SELECT id FROM purchase_orders WHERE po_number = %s"
                existing = self.db.fetch_one(check_query, (self.po_number_label.text(),))
                if existing:
                    QMessageBox.warning(self, "Duplicate", "PO number already exists!")
                    return
                
                # Insert new PO
                query = """
                    INSERT INTO purchase_orders (
                        po_number, supplier_id, order_date, expected_delivery,
                        status, total_items, total_amount, discount, tax,
                        grand_total, created_by, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor = self.db.execute_query(query, (
                    self.po_number_label.text(),
                    self.supplier_combo.currentData(),
                    self.order_date.date().toString('yyyy-MM-dd'),
                    self.expected_date.date().toString('yyyy-MM-dd'),
                    'draft',
                    len(self.po_items),
                    sum(item['total_cost'] for item in self.po_items),
                    self.discount_input.value(),
                    self.tax_input.value(),
                    grand_total,
                    self.user['id'],
                    self.po_notes.toPlainText()
                ))
                
                if cursor:
                    self.current_po = {'id': cursor.lastrowid, 'po_number': self.po_number_label.text()}
            
            # Insert items
            if self.current_po:
                for item in self.po_items:
                    item_query = """
                        INSERT INTO purchase_order_items 
                        (po_id, product_id, quantity, unit_cost, total_cost, status)
                        VALUES (%s, %s, %s, %s, %s, 'pending')
                    """
                    self.db.execute_query(item_query, (
                        self.current_po['id'],
                        item['product_id'],
                        item['quantity'],
                        item['unit_cost'],
                        item['total_cost']
                    ))
            
            QMessageBox.information(self, "Success", f"PO {self.po_number_label.text()} saved successfully!")
            self.load_purchase_orders()
            
            # Enable send button
            self.send_po_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PO: {str(e)}")
    
    def send_to_supplier(self):
        if not self.current_po:
            return
        
        reply = QMessageBox.question(self, "Send PO", 
                                    "Mark this PO as sent to supplier?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                query = "UPDATE purchase_orders SET status = 'sent' WHERE id = %s"
                self.db.execute_query(query, (self.current_po['id'],))
                
                self.po_status_label.setText("Sent")
                self.po_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
                
                self.save_po_btn.setEnabled(False)
                self.send_po_btn.setEnabled(False)
                self.receive_po_btn.setEnabled(True)
                
                QMessageBox.information(self, "Success", "PO marked as sent to supplier.")
                self.load_purchase_orders()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update PO: {str(e)}")
    
    def receive_order(self):
        if not self.current_po:
            return
        
        dialog = ReceiveOrderDialog(self.current_po, self.po_items, self)
        if dialog.exec_():
            self.load_po_details(self.current_po['po_number'])
            self.load_purchase_orders()
    
    def validate_po_form(self):
        if not self.supplier_combo.currentData():
            QMessageBox.warning(self, "Validation", "Please select a supplier.")
            return False
        
        if not self.po_items:
            QMessageBox.warning(self, "Validation", "Please add at least one item.")
            return False
        
        return True
    
    def view_po(self, po):
        self.load_po_details(po['po_number'])


class PurchaseProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.selected_product = None
        self.quantity = 1
        self.init_ui()
        self.load_products()
        self.load_categories()
    
    def init_ui(self):
        self.setWindowTitle("Add Product to Purchase Order")
        self.setGeometry(300, 300, 700, 500)
        
        layout = QVBoxLayout(self)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or barcode...")
        self.search_input.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.load_products)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels([
            "Barcode", "Product", "Current Stock", "Cost Price", "Category"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.products_table)
        
        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        qty_layout.addWidget(self.qty_spin)
        qty_layout.addStretch()
        layout.addLayout(qty_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("Add to PO")
        select_btn.clicked.connect(self.accept)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_categories(self):
        query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL"
        categories = self.db.fetch_all(query)
        for cat in categories:
            self.category_filter.addItem(cat['category'])
    
    def load_products(self):
        search = self.search_input.text()
        category = self.category_filter.currentText()
        
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE %s OR barcode LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        if category and category != "All Categories":
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY name LIMIT 50"
        
        products = self.db.fetch_all(query, params)
        
        self.products_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product['barcode']))
            self.products_table.setItem(i, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(i, 2, QTableWidgetItem(str(product['quantity'])))
            self.products_table.setItem(i, 3, QTableWidgetItem(format_currency(product['cost_price'])))
            self.products_table.setItem(i, 4, QTableWidgetItem(product['category'] or '-'))
    
    def select_product(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        query = "SELECT * FROM products WHERE barcode = %s"
        self.selected_product = self.db.fetch_one(query, (barcode,))
        self.quantity = self.qty_spin.value()
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product, self.quantity


class ReceiveOrderDialog(QDialog):
    def __init__(self, po, items, parent=None):
        super().__init__(parent)
        self.po = po
        self.items = items
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Receive Order - {self.po['po_number']}")
        self.setGeometry(400, 300, 600, 500)
        
        layout = QVBoxLayout(self)
        
        # PO Info
        info_group = QGroupBox("Order Information")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("PO Number:"), 0, 0)
        info_layout.addWidget(QLabel(self.po['po_number']), 0, 1)
        
        info_layout.addWidget(QLabel("Supplier:"), 0, 2)
        info_layout.addWidget(QLabel(self.po.get('supplier_name', '-')), 0, 3)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Items to receive
        items_group = QGroupBox("Items to Receive")
        items_layout = QVBoxLayout()
        
        self.receive_table = QTableWidget()
        self.receive_table.setColumnCount(5)
        self.receive_table.setHorizontalHeaderLabels([
            "Product", "Ordered", "Received", "Now Receiving", "Status"
        ])
        self.receive_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.receive_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Populate table
        self.receive_table.setRowCount(len(self.items))
        for i, item in enumerate(self.items):
            self.receive_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            self.receive_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.receive_table.setItem(i, 2, QTableWidgetItem(str(item['received_quantity'])))
            
            # Receiving quantity
            receive_spin = QSpinBox()
            receive_spin.setRange(0, item['quantity'] - item['received_quantity'])
            receive_spin.setValue(item['quantity'] - item['received_quantity'])
            receive_spin.valueChanged.connect(lambda v, idx=i: self.update_receive_status(idx, v))
            self.receive_table.setCellWidget(i, 3, receive_spin)
            
            # Status
            remaining = item['quantity'] - item['received_quantity']
            if remaining == 0:
                status = "Completed"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#4CAF50'))
            else:
                status = f"Pending ({remaining})"
                status_item = QTableWidgetItem(status)
            self.receive_table.setItem(i, 4, status_item)
        
        # Notes
        notes_group = QGroupBox("Receiving Notes")
        notes_layout = QVBoxLayout()
        self.receive_notes = QTextEdit()
        self.receive_notes.setMaximumHeight(80)
        notes_layout.addWidget(self.receive_notes)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        receive_btn = QPushButton("✅ Complete Receiving")
        receive_btn.clicked.connect(self.complete_receiving)
        button_layout.addWidget(receive_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def update_receive_status(self, index, value):
        if value > 0:
            status_item = QTableWidgetItem(f"Receiving {value}")
            status_item.setForeground(QColor('#2196F3'))
            self.receive_table.setItem(index, 4, status_item)
    
    def complete_receiving(self):
        try:
            total_received = 0
            all_completed = True
            
            for i, item in enumerate(self.items):
                receive_spin = self.receive_table.cellWidget(i, 3)
                receiving_qty = receive_spin.value() if receive_spin else 0
                
                if receiving_qty > 0:
                    total_received += 1
                    
                    # Update received quantity
                    new_received = item['received_quantity'] + receiving_qty
                    
                    # Determine item status
                    if new_received >= item['quantity']:
                        item_status = 'received'
                    else:
                        item_status = 'partial'
                        all_completed = False
                    
                    # Update in database
                    query = """
                        UPDATE purchase_order_items 
                        SET received_quantity = %s, status = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(query, (new_received, item_status, item['id']))
                    
                    # Update product stock
                    if receiving_qty > 0:
                        stock_query = """
                            UPDATE products 
                            SET quantity = quantity + %s 
                            WHERE id = %s
                        """
                        self.db.execute_query(stock_query, (receiving_qty, item['product_id']))
            
            # Update PO status
            if all_completed:
                po_status = 'received'
            elif total_received > 0:
                po_status = 'partial'
            else:
                po_status = 'confirmed'
            
            po_query = "UPDATE purchase_orders SET status = %s WHERE id = %s"
            self.db.execute_query(po_query, (po_status, self.po['id']))
            
            QMessageBox.information(self, "Success", "Receiving completed successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to complete receiving: {str(e)}")
