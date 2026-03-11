from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QDateEdit, QMessageBox, QDialog, QTabWidget,
                           QSplitter, QFrame)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from datetime import datetime

class GoodsInwardModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_receipt = None
        self.received_items = []
        self.init_ui()
        self.load_receipts()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📦 Goods Inward - Purchase Receiving")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Receipts list
        left_panel = self.create_receipts_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Receiving form
        right_panel = self.create_receiving_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.new_receipt_btn = QPushButton("➕ New Receipt")
        self.new_receipt_btn.clicked.connect(self.new_receipt)
        buttons_layout.addWidget(self.new_receipt_btn)
        
        self.save_btn = QPushButton("💾 Save Receipt")
        self.save_btn.clicked.connect(self.save_receipt)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)
        
        self.complete_btn = QPushButton("✅ Complete Receiving")
        self.complete_btn.clicked.connect(self.complete_receiving)
        self.complete_btn.setEnabled(False)
        buttons_layout.addWidget(self.complete_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_receipts)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def create_receipts_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'pending', 'completed', 'cancelled'])
        self.status_filter.currentTextChanged.connect(self.load_receipts)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by invoice # or supplier...")
        self.search_box.textChanged.connect(self.load_receipts)
        filter_layout.addWidget(self.search_box)
        
        layout.addLayout(filter_layout)
        
        # Receipts table
        self.receipts_table = QTableWidget()
        self.receipts_table.setColumnCount(6)
        self.receipts_table.setHorizontalHeaderLabels([
            "Invoice #", "Supplier", "Date", "Items", "Amount", "Status"
        ])
        self.receipts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.receipts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.receipts_table.itemClicked.connect(self.on_receipt_selected)
        layout.addWidget(self.receipts_table)
        
        return panel
    
    def create_receiving_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Receipt header form
        header_group = QGroupBox("Receipt Details")
        header_layout = QGridLayout()
        
        # Row 1
        header_layout.addWidget(QLabel("Invoice Number:*"), 0, 0)
        self.invoice_input = QLineEdit()
        self.invoice_input.setPlaceholderText("Supplier Invoice #")
        header_layout.addWidget(self.invoice_input, 0, 1)
        
        header_layout.addWidget(QLabel("PO Number:"), 0, 2)
        self.po_input = QLineEdit()
        self.po_input.setPlaceholderText("Purchase Order #")
        header_layout.addWidget(self.po_input, 0, 3)
        
        # Row 2
        header_layout.addWidget(QLabel("Supplier:*"), 1, 0)
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Supplier Name")
        header_layout.addWidget(self.supplier_input, 1, 1)
        
        header_layout.addWidget(QLabel("Received Date:*"), 1, 2)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        header_layout.addWidget(self.date_input, 1, 3)
        
        # Row 3
        header_layout.addWidget(QLabel("Supplier Invoice:"), 2, 0)
        self.supplier_invoice_input = QLineEdit()
        self.supplier_invoice_input.setPlaceholderText("Supplier's Invoice Ref")
        header_layout.addWidget(self.supplier_invoice_input, 2, 1)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items section
        items_group = QGroupBox("Received Items")
        items_layout = QVBoxLayout()
        
        # Add item controls
        add_item_layout = QHBoxLayout()
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search product by name or barcode...")
        add_item_layout.addWidget(self.product_search)
        
        self.add_item_btn = QPushButton("➕ Add Item")
        self.add_item_btn.clicked.connect(self.show_product_dialog)
        add_item_layout.addWidget(self.add_item_btn)
        
        items_layout.addLayout(add_item_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Product", "Batch #", "Ordered", "Received", "Unit Cost", "Total", "Action"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        
        self.total_items_label = QLabel("Total Items: 0")
        summary_layout.addWidget(self.total_items_label)
        
        self.total_amount_label = QLabel("Total Amount: ₹ 0.00")
        self.total_amount_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_amount_label.setStyleSheet("color: #2196F3;")
        summary_layout.addWidget(self.total_amount_label)
        
        summary_layout.addStretch()
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        return panel
    
    def load_receipts(self):
        try:
            status = self.status_filter.currentText()
            search = self.search_box.text()
            
            query = """
                SELECT * FROM goods_inward 
                WHERE 1=1
            """
            params = []
            
            if status != 'All':
                query += " AND status = %s"
                params.append(status.lower())
            
            if search:
                query += " AND (invoice_number LIKE %s OR supplier_name LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            query += " ORDER BY received_date DESC"
            
            receipts = self.db.fetch_all(query, params)
            
            self.receipts_table.setRowCount(len(receipts))
            for i, receipt in enumerate(receipts):
                self.receipts_table.setItem(i, 0, QTableWidgetItem(receipt['invoice_number']))
                self.receipts_table.setItem(i, 1, QTableWidgetItem(receipt['supplier_name']))
                self.receipts_table.setItem(i, 2, QTableWidgetItem(str(receipt['received_date'])))
                self.receipts_table.setItem(i, 3, QTableWidgetItem(str(receipt['total_items'])))
                self.receipts_table.setItem(i, 4, QTableWidgetItem(format_currency(receipt['total_amount'])))
                
                status_item = QTableWidgetItem(receipt['status'])
                if receipt['status'] == 'completed':
                    status_item.setForeground(QColor('#4CAF50'))
                elif receipt['status'] == 'cancelled':
                    status_item.setForeground(QColor('#F44336'))
                self.receipts_table.setItem(i, 5, status_item)
                
        except Exception as e:
            print(f"Error loading receipts: {e}")
    
    def on_receipt_selected(self, item):
        row = item.row()
        invoice = self.receipts_table.item(row, 0).text()
        self.load_receipt_details(invoice)
    
    def load_receipt_details(self, invoice):
        try:
            query = "SELECT * FROM goods_inward WHERE invoice_number = %s"
            receipt = self.db.fetch_one(query, (invoice,))
            
            if receipt:
                self.current_receipt = receipt
                self.invoice_input.setText(receipt['invoice_number'])
                self.po_input.setText(receipt['po_number'] or '')
                self.supplier_input.setText(receipt['supplier_name'])
                self.date_input.setDate(QDate.fromString(str(receipt['received_date']), 'yyyy-MM-dd'))
                self.supplier_invoice_input.setText(receipt['supplier_invoice'] or '')
                self.notes_input.setText(receipt['notes'] or '')
                
                # Load items
                items_query = "SELECT * FROM goods_inward_items WHERE goods_inward_id = %s"
                items = self.db.fetch_all(items_query, (receipt['id'],))
                
                self.received_items = []
                for item in items:
                    product_query = "SELECT name FROM products WHERE id = %s"
                    product = self.db.fetch_one(product_query, (item['product_id'],))
                    
                    self.received_items.append({
                        'id': item['id'],
                        'product_id': item['product_id'],
                        'product_name': product['name'] if product else 'Unknown',
                        'batch_number': item['batch_number'],
                        'quantity_ordered': item['quantity_ordered'],
                        'quantity_received': item['quantity_received'],
                        'unit_cost': float(item['unit_cost']),
                        'total_cost': float(item['total_cost']),
                        'expiry_date': item['expiry_date']
                    })
                
                self.update_items_table()
                
                # Enable/disable buttons based on status
                if receipt['status'] == 'pending':
                    self.save_btn.setEnabled(True)
                    self.complete_btn.setEnabled(True)
                else:
                    self.save_btn.setEnabled(False)
                    self.complete_btn.setEnabled(False)
                    
        except Exception as e:
            print(f"Error loading receipt details: {e}")
    
    def new_receipt(self):
        self.current_receipt = None
        self.received_items = []
        self.invoice_input.clear()
        self.po_input.clear()
        self.supplier_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.supplier_invoice_input.clear()
        self.notes_input.clear()
        self.update_items_table()
        
        self.save_btn.setEnabled(True)
        self.complete_btn.setEnabled(True)
    
    def show_product_dialog(self):
        dialog = ProductSearchDialog(self)
        if dialog.exec_():
            product, quantity = dialog.get_selected_product()
            if product:
                self.add_item(product, quantity)
    
    def add_item(self, product, quantity):
        # Check if product already added
        for item in self.received_items:
            if item['product_id'] == product['id']:
                # Update existing item
                item['quantity_ordered'] += quantity
                item['quantity_received'] += quantity
                item['total_cost'] = item['quantity_received'] * item['unit_cost']
                self.update_items_table()
                self.calculate_totals()
                return
        
        # Add new item
        dialog = ItemDetailsDialog(product, quantity, self)
        if dialog.exec_():
            item_data = dialog.get_item_data()
            self.received_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'batch_number': item_data['batch_number'],
                'quantity_ordered': item_data['quantity_ordered'],
                'quantity_received': item_data['quantity_received'],
                'unit_cost': item_data['unit_cost'],
                'total_cost': item_data['total_cost'],
                'expiry_date': item_data['expiry_date']
            })
            self.update_items_table()
            self.calculate_totals()
    
    def update_items_table(self):
        self.items_table.setRowCount(len(self.received_items))
        for i, item in enumerate(self.received_items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(i, 1, QTableWidgetItem(item['batch_number'] or '-'))
            self.items_table.setItem(i, 2, QTableWidgetItem(str(item['quantity_ordered'])))
            self.items_table.setItem(i, 3, QTableWidgetItem(str(item['quantity_received'])))
            self.items_table.setItem(i, 4, QTableWidgetItem(format_currency(item['unit_cost'])))
            self.items_table.setItem(i, 5, QTableWidgetItem(format_currency(item['total_cost'])))
            
            remove_btn = QPushButton("❌")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.items_table.setCellWidget(i, 6, remove_btn)
    
    def remove_item(self, index):
        if 0 <= index < len(self.received_items):
            del self.received_items[index]
            self.update_items_table()
            self.calculate_totals()
    
    def calculate_totals(self):
        total_items = len(self.received_items)
        total_amount = sum(item['total_cost'] for item in self.received_items)
        
        self.total_items_label.setText(f"Total Items: {total_items}")
        self.total_amount_label.setText(f"Total Amount: {format_currency(total_amount)}")
    
    def save_receipt(self):
        if not self.validate_form():
            return
        
        try:
            invoice = self.invoice_input.text()
            total_amount = sum(item['total_cost'] for item in self.received_items)
            
            if self.current_receipt:
                # Update existing receipt
                query = """
                    UPDATE goods_inward 
                    SET po_number = %s, supplier_name = %s, received_date = %s,
                        supplier_invoice = %s, total_items = %s, total_amount = %s,
                        notes = %s
                    WHERE id = %s
                """
                self.db.execute_query(query, (
                    self.po_input.text(),
                    self.supplier_input.text(),
                    self.date_input.date().toString('yyyy-MM-dd'),
                    self.supplier_invoice_input.text(),
                    len(self.received_items),
                    total_amount,
                    self.notes_input.toPlainText(),
                    self.current_receipt['id']
                ))
                
                # Delete old items
                del_query = "DELETE FROM goods_inward_items WHERE goods_inward_id = %s"
                self.db.execute_query(del_query, (self.current_receipt['id'],))
                
            else:
                # Check if invoice exists
                check_query = "SELECT id FROM goods_inward WHERE invoice_number = %s"
                existing = self.db.fetch_one(check_query, (invoice,))
                if existing:
                    QMessageBox.warning(self, "Duplicate", "Invoice number already exists!")
                    return
                
                # Insert new receipt
                query = """
                    INSERT INTO goods_inward (invoice_number, po_number, supplier_name,
                        received_date, supplier_invoice, received_by, total_items, 
                        total_amount, notes, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                """
                cursor = self.db.execute_query(query, (
                    invoice,
                    self.po_input.text(),
                    self.supplier_input.text(),
                    self.date_input.date().toString('yyyy-MM-dd'),
                    self.supplier_invoice_input.text(),
                    self.user['id'],
                    len(self.received_items),
                    total_amount,
                    self.notes_input.toPlainText()
                ))
                
                if cursor:
                    self.current_receipt = {'id': cursor.lastrowid}
            
            # Insert items
            if self.current_receipt:
                for item in self.received_items:
                    item_query = """
                        INSERT INTO goods_inward_items 
                        (goods_inward_id, product_id, quantity_received, quantity_ordered,
                         unit_cost, total_cost, expiry_date, batch_number)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    self.db.execute_query(item_query, (
                        self.current_receipt['id'],
                        item['product_id'],
                        item['quantity_received'],
                        item['quantity_ordered'],
                        item['unit_cost'],
                        item['total_cost'],
                        item['expiry_date'],
                        item['batch_number']
                    ))
            
            QMessageBox.information(self, "Success", "Receipt saved successfully!")
            self.load_receipts()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save receipt: {str(e)}")
    
    def complete_receiving(self):
        if not self.current_receipt:
            QMessageBox.warning(self, "No Receipt", "Please save the receipt first.")
            return
        
        reply = QMessageBox.question(self, "Complete Receiving", 
                                    "Are you sure you want to complete this receiving? "
                                    "This will update inventory levels.",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Update status
                query = "UPDATE goods_inward SET status = 'completed' WHERE id = %s"
                self.db.execute_query(query, (self.current_receipt['id'],))
                
                # Update product quantities
                for item in self.received_items:
                    update_query = """
                        UPDATE products 
                        SET quantity = quantity + %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (item['quantity_received'], item['product_id']))
                    
                    # Update expiry date if provided
                    if item['expiry_date']:
                        expiry_query = """
                            UPDATE products 
                            SET expiry_date = %s 
                            WHERE id = %s AND (expiry_date IS NULL OR expiry_date > %s)
                        """
                        self.db.execute_query(expiry_query, (item['expiry_date'], item['product_id'], item['expiry_date']))
                
                QMessageBox.information(self, "Success", "Receiving completed and inventory updated!")
                self.load_receipts()
                self.load_receipt_details(self.current_receipt['invoice_number'])
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to complete receiving: {str(e)}")
    
    def validate_form(self):
        if not self.invoice_input.text():
            QMessageBox.warning(self, "Validation", "Invoice number is required.")
            return False
        
        if not self.supplier_input.text():
            QMessageBox.warning(self, "Validation", "Supplier name is required.")
            return False
        
        if not self.received_items:
            QMessageBox.warning(self, "Validation", "Please add at least one item.")
            return False
        
        return True


class ItemDetailsDialog(QDialog):
    def __init__(self, product, default_quantity, parent=None):
        super().__init__(parent)
        self.product = product
        self.default_quantity = default_quantity
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Item Details - {self.product['name']}")
        self.setGeometry(400, 300, 400, 300)
        
        layout = QVBoxLayout(self)
        
        # Product info
        info_label = QLabel(f"Product: {self.product['name']}\nBarcode: {self.product['barcode']}")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.ordered_spin = QSpinBox()
        self.ordered_spin.setRange(1, 9999)
        self.ordered_spin.setValue(self.default_quantity)
        form_layout.addRow("Quantity Ordered:", self.ordered_spin)
        
        self.received_spin = QSpinBox()
        self.received_spin.setRange(0, 9999)
        self.received_spin.setValue(self.default_quantity)
        form_layout.addRow("Quantity Received:", self.received_spin)
        
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 999999)
        self.cost_spin.setValue(float(self.product['cost_price'] or 0))
        self.cost_spin.setPrefix("₹ ")
        form_layout.addRow("Unit Cost:", self.cost_spin)
        
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("Batch/Lot Number")
        form_layout.addRow("Batch Number:", self.batch_input)
        
        self.expiry_date = QDateEdit()
        self.expiry_date.setDate(QDate.currentDate().addMonths(6))
        self.expiry_date.setCalendarPopup(True)
        form_layout.addRow("Expiry Date:", self.expiry_date)
        
        layout.addLayout(form_layout)
        
        # Total
        self.total_label = QLabel()
        self.update_total()
        layout.addWidget(self.total_label)
        
        # Connect signals
        self.received_spin.valueChanged.connect(self.update_total)
        self.cost_spin.valueChanged.connect(self.update_total)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def update_total(self):
        total = self.received_spin.value() * self.cost_spin.value()
        self.total_label.setText(f"Total: {format_currency(total)}")
    
    def get_item_data(self):
        return {
            'quantity_ordered': self.ordered_spin.value(),
            'quantity_received': self.received_spin.value(),
            'unit_cost': self.cost_spin.value(),
            'total_cost': self.received_spin.value() * self.cost_spin.value(),
            'batch_number': self.batch_input.text(),
            'expiry_date': self.expiry_date.date().toString('yyyy-MM-dd')
        }


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
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or barcode...")
        self.search_input.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Barcode", "Product", "Current Stock"])
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
            query = "SELECT * FROM products WHERE name LIKE %s OR barcode LIKE %s LIMIT 20"
            search_term = f"%{search}%"
            products = self.db.fetch_all(query, (search_term, search_term))
        else:
            query = "SELECT * FROM products LIMIT 20"
            products = self.db.fetch_all(query)
        
        self.products_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product['barcode']))
            self.products_table.setItem(i, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(i, 2, QTableWidgetItem(str(product['quantity'])))
    
    def select_product(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        query = "SELECT * FROM products WHERE barcode = %s"
        self.selected_product = self.db.fetch_one(query, (barcode,))
        self.quantity = self.qty_spin.value()
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product, self.quantity
