from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QDateEdit, QMessageBox, QDialog, QTabWidget,
                           QSplitter, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, generate_invoice_number
from datetime import datetime
import uuid

class StockAuditModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_audit = None
        self.audit_items = []
        self.init_ui()
        self.load_audits()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📊 Stock Audit & Inventory Verification")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Audit list
        left_panel = self.create_audit_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Audit form
        right_panel = self.create_audit_form_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.new_audit_btn = QPushButton("➕ New Audit")
        self.new_audit_btn.clicked.connect(self.new_audit)
        buttons_layout.addWidget(self.new_audit_btn)
        
        self.start_audit_btn = QPushButton("▶️ Start Audit")
        self.start_audit_btn.clicked.connect(self.start_audit)
        self.start_audit_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_audit_btn)
        
        self.save_audit_btn = QPushButton("💾 Save Progress")
        self.save_audit_btn.clicked.connect(self.save_audit_progress)
        self.save_audit_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_audit_btn)
        
        self.complete_audit_btn = QPushButton("✅ Complete Audit")
        self.complete_audit_btn.clicked.connect(self.complete_audit)
        self.complete_audit_btn.setEnabled(False)
        buttons_layout.addWidget(self.complete_audit_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_audits)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def create_audit_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'draft', 'in_progress', 'completed', 'cancelled'])
        self.status_filter.currentTextChanged.connect(self.load_audits)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by audit #...")
        self.search_box.textChanged.connect(self.load_audits)
        filter_layout.addWidget(self.search_box)
        
        layout.addLayout(filter_layout)
        
        # Audits table
        self.audits_table = QTableWidget()
        self.audits_table.setColumnCount(7)
        self.audits_table.setHorizontalHeaderLabels([
            "Audit #", "Date", "Auditor", "Items", "Discrepancies", "Value Diff", "Status"
        ])
        self.audits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audits_table.itemClicked.connect(self.on_audit_selected)
        layout.addWidget(self.audits_table)
        
        return panel
    
    def create_audit_form_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Audit header
        header_group = QGroupBox("Audit Details")
        header_layout = QGridLayout()
        
        header_layout.addWidget(QLabel("Audit Number:"), 0, 0)
        self.audit_number_label = QLabel("-")
        header_layout.addWidget(self.audit_number_label, 0, 1)
        
        header_layout.addWidget(QLabel("Audit Date:"), 0, 2)
        self.audit_date_label = QLabel(QDate.currentDate().toString('dd/MM/yyyy'))
        header_layout.addWidget(self.audit_date_label, 0, 3)
        
        header_layout.addWidget(QLabel("Status:"), 1, 0)
        self.audit_status_label = QLabel("Draft")
        self.audit_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        header_layout.addWidget(self.audit_status_label, 1, 1)
        
        header_layout.addWidget(QLabel("Progress:"), 1, 2)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        header_layout.addWidget(self.progress_bar, 1, 3)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items section
        items_group = QGroupBox("Audit Items")
        items_layout = QVBoxLayout()
        
        # Search and filters
        search_layout = QHBoxLayout()
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search product to audit...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.search_products)
        search_layout.addWidget(self.category_filter)
        
        self.add_product_btn = QPushButton("➕ Add to Audit")
        self.add_product_btn.clicked.connect(self.show_product_dialog)
        search_layout.addWidget(self.add_product_btn)
        
        items_layout.addLayout(search_layout)
        
        # Products to audit table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels([
            "Product", "System Qty", "Physical Qty", "Discrepancy", "Status"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.products_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Summary
        summary_group = QGroupBox("Audit Summary")
        summary_layout = QGridLayout()
        
        summary_layout.addWidget(QLabel("Total Items Audited:"), 0, 0)
        self.total_items_label = QLabel("0")
        summary_layout.addWidget(self.total_items_label, 0, 1)
        
        summary_layout.addWidget(QLabel("Items with Discrepancy:"), 0, 2)
        self.discrepancy_count_label = QLabel("0")
        self.discrepancy_count_label.setStyleSheet("color: #F44336;")
        summary_layout.addWidget(self.discrepancy_count_label, 0, 3)
        
        summary_layout.addWidget(QLabel("Total Discrepancy Value:"), 1, 0)
        self.discrepancy_value_label = QLabel("₹ 0.00")
        self.discrepancy_value_label.setStyleSheet("color: #F44336; font-weight: bold;")
        summary_layout.addWidget(self.discrepancy_value_label, 1, 1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        self.audit_notes = QTextEdit()
        self.audit_notes.setMaximumHeight(80)
        notes_layout.addWidget(self.audit_notes)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        return panel
    
    def load_audits(self):
        try:
            status = self.status_filter.currentText()
            search = self.search_box.text()
            
            query = """
                SELECT sa.*, u.username as auditor_name
                FROM stock_audits sa
                LEFT JOIN users u ON sa.conducted_by = u.id
                WHERE 1=1
            """
            params = []
            
            if status != 'All':
                query += " AND sa.status = %s"
                params.append(status.lower())
            
            if search:
                query += " AND sa.audit_number LIKE %s"
                params.append(f"%{search}%")
            
            query += " ORDER BY sa.created_at DESC"
            
            audits = self.db.fetch_all(query, params)
            
            self.audits_table.setRowCount(len(audits))
            for i, audit in enumerate(audits):
                self.audits_table.setItem(i, 0, QTableWidgetItem(audit['audit_number']))
                self.audits_table.setItem(i, 1, QTableWidgetItem(str(audit['audit_date'])))
                self.audits_table.setItem(i, 2, QTableWidgetItem(audit.get('auditor_name', '-')))
                self.audits_table.setItem(i, 3, QTableWidgetItem(str(audit['total_items_audited'])))
                self.audits_table.setItem(i, 4, QTableWidgetItem(str(audit['total_discrepancies'])))
                self.audits_table.setItem(i, 5, QTableWidgetItem(format_currency(audit['total_value_discrepancy'])))
                
                status_item = QTableWidgetItem(audit['status'].replace('_', ' ').title())
                if audit['status'] == 'completed':
                    status_item.setForeground(QColor('#4CAF50'))
                elif audit['status'] == 'in_progress':
                    status_item.setForeground(QColor('#FF9800'))
                elif audit['status'] == 'cancelled':
                    status_item.setForeground(QColor('#F44336'))
                self.audits_table.setItem(i, 6, status_item)
                
        except Exception as e:
            print(f"Error loading audits: {e}")
    
    def on_audit_selected(self, item):
        row = item.row()
        audit_number = self.audits_table.item(row, 0).text()
        self.load_audit_details(audit_number)
    
    def load_audit_details(self, audit_number):
        try:
            query = "SELECT * FROM stock_audits WHERE audit_number = %s"
            audit = self.db.fetch_one(query, (audit_number,))
            
            if audit:
                self.current_audit = audit
                self.audit_number_label.setText(audit['audit_number'])
                self.audit_date_label.setText(str(audit['audit_date']))
                self.audit_status_label.setText(audit['status'].replace('_', ' ').title())
                self.audit_notes.setText(audit['notes'] or '')
                
                # Set status color
                if audit['status'] == 'completed':
                    self.audit_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                elif audit['status'] == 'in_progress':
                    self.audit_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                elif audit['status'] == 'draft':
                    self.audit_status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
                
                # Load audit items
                items_query = """
                    SELECT sai.*, p.name as product_name
                    FROM stock_audit_items sai
                    LEFT JOIN products p ON sai.product_id = p.id
                    WHERE sai.audit_id = %s
                """
                items = self.db.fetch_all(items_query, (audit['id'],))
                
                self.audit_items = []
                for item in items:
                    self.audit_items.append({
                        'id': item['id'],
                        'product_id': item['product_id'],
                        'product_name': item['product_name'],
                        'system_quantity': item['system_quantity'],
                        'physical_quantity': item['physical_quantity'],
                        'discrepancy': item['discrepancy'],
                        'unit_cost': float(item['unit_cost']),
                        'discrepancy_value': float(item['discrepancy_value']),
                        'status': item['status']
                    })
                
                self.update_audit_table()
                self.update_summary()
                
                # Update progress
                total_items = len(self.audit_items)
                verified_items = sum(1 for i in self.audit_items if i['status'] == 'verified')
                progress = (verified_items / total_items * 100) if total_items > 0 else 0
                self.progress_bar.setValue(int(progress))
                
                # Enable/disable buttons based on status
                if audit['status'] == 'draft':
                    self.start_audit_btn.setEnabled(True)
                    self.save_audit_btn.setEnabled(False)
                    self.complete_audit_btn.setEnabled(False)
                elif audit['status'] == 'in_progress':
                    self.start_audit_btn.setEnabled(False)
                    self.save_audit_btn.setEnabled(True)
                    self.complete_audit_btn.setEnabled(True)
                else:
                    self.start_audit_btn.setEnabled(False)
                    self.save_audit_btn.setEnabled(False)
                    self.complete_audit_btn.setEnabled(False)
                
        except Exception as e:
            print(f"Error loading audit details: {e}")
    
    def new_audit(self):
        self.current_audit = None
        self.audit_items = []
        
        audit_number = f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.audit_number_label.setText(audit_number)
        self.audit_date_label.setText(QDate.currentDate().toString('dd/MM/yyyy'))
        self.audit_status_label.setText("Draft")
        self.audit_status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
        self.audit_notes.clear()
        self.progress_bar.setValue(0)
        
        self.update_audit_table()
        self.update_summary()
        
        self.start_audit_btn.setEnabled(True)
        self.save_audit_btn.setEnabled(False)
        self.complete_audit_btn.setEnabled(False)
    
    def start_audit(self):
        if not self.current_audit:
            # Create new audit
            try:
                audit_number = self.audit_number_label.text()
                
                query = """
                    INSERT INTO stock_audits (audit_number, audit_date, conducted_by, status)
                    VALUES (%s, %s, %s, 'in_progress')
                """
                cursor = self.db.execute_query(query, (
                    audit_number,
                    QDate.currentDate().toString('yyyy-MM-dd'),
                    self.user['id']
                ))
                
                if cursor:
                    self.current_audit = {
                        'id': cursor.lastrowid,
                        'audit_number': audit_number,
                        'status': 'in_progress'
                    }
                    
                    self.audit_status_label.setText("In Progress")
                    self.audit_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                    
                    self.start_audit_btn.setEnabled(False)
                    self.save_audit_btn.setEnabled(True)
                    self.complete_audit_btn.setEnabled(True)
                    
                    QMessageBox.information(self, "Success", "Audit started successfully!")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start audit: {str(e)}")
    
    def show_product_dialog(self):
        dialog = ProductAuditDialog(self)
        if dialog.exec_():
            product = dialog.get_selected_product()
            if product:
                self.add_to_audit(product)
    
    def add_to_audit(self, product):
        # Check if product already in audit
        for item in self.audit_items:
            if item['product_id'] == product['id']:
                QMessageBox.warning(self, "Duplicate", "Product already in audit list.")
                return
        
        # Add to audit
        self.audit_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'system_quantity': product['quantity'],
            'physical_quantity': product['quantity'],  # Start with system quantity
            'discrepancy': 0,
            'unit_cost': float(product['cost_price'] or 0),
            'discrepancy_value': 0,
            'status': 'pending'
        })
        
        self.update_audit_table()
        self.update_summary()
        
        # Save to database if audit is in progress
        if self.current_audit and self.current_audit['status'] == 'in_progress':
            self.save_audit_item(product)
    
    def save_audit_item(self, product):
        try:
            query = """
                INSERT INTO stock_audit_items 
                (audit_id, product_id, system_quantity, physical_quantity, 
                 discrepancy, unit_cost, discrepancy_value, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """
            self.db.execute_query(query, (
                self.current_audit['id'],
                product['id'],
                product['quantity'],
                product['quantity'],
                0,
                product['cost_price'] or 0,
                0
            ))
            
        except Exception as e:
            print(f"Error saving audit item: {e}")
    
    def update_audit_table(self):
        self.products_table.setRowCount(len(self.audit_items))
        for i, item in enumerate(self.audit_items):
            self.products_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            self.products_table.setItem(i, 1, QTableWidgetItem(str(item['system_quantity'])))
            
            # Physical quantity with edit button
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            
            qty_spin = QSpinBox()
            qty_spin.setRange(0, 99999)
            qty_spin.setValue(item['physical_quantity'])
            qty_spin.valueChanged.connect(lambda value, idx=i: self.update_physical_qty(idx, value))
            qty_layout.addWidget(qty_spin)
            
            self.products_table.setCellWidget(i, 2, qty_widget)
            
            # Discrepancy
            discrepancy = item['physical_quantity'] - item['system_quantity']
            discrepancy_item = QTableWidgetItem(str(discrepancy))
            if discrepancy != 0:
                discrepancy_item.setForeground(QColor('#F44336'))
                discrepancy_item.setBackground(QColor('#FFEBEE'))
            self.products_table.setItem(i, 3, discrepancy_item)
            
            # Status
            status_item = QTableWidgetItem(item['status'].title())
            if item['status'] == 'verified':
                status_item.setForeground(QColor('#4CAF50'))
            self.products_table.setItem(i, 4, status_item)
    
    def update_physical_qty(self, index, value):
        if 0 <= index < len(self.audit_items):
            item = self.audit_items[index]
            old_qty = item['physical_quantity']
            item['physical_quantity'] = value
            
            # Calculate discrepancy
            discrepancy = value - item['system_quantity']
            item['discrepancy'] = discrepancy
            item['discrepancy_value'] = discrepancy * item['unit_cost']
            
            # Update table
            discrepancy_item = QTableWidgetItem(str(discrepancy))
            if discrepancy != 0:
                discrepancy_item.setForeground(QColor('#F44336'))
                discrepancy_item.setBackground(QColor('#FFEBEE'))
            self.products_table.setItem(index, 3, discrepancy_item)
            
            # Auto-mark as pending when quantity changes
            if item['status'] == 'verified':
                item['status'] = 'pending'
                status_item = QTableWidgetItem('Pending')
                status_item.setForeground(QColor('#FF9800'))
                self.products_table.setItem(index, 4, status_item)
            
            self.update_summary()
            
            # Update database if audit in progress
            if self.current_audit and self.current_audit['status'] == 'in_progress' and 'id' in item:
                self.update_audit_item_in_db(item)
    
    def update_audit_item_in_db(self, item):
        try:
            query = """
                UPDATE stock_audit_items 
                SET physical_quantity = %s, discrepancy = %s, 
                    discrepancy_value = %s, status = %s
                WHERE id = %s
            """
            self.db.execute_query(query, (
                item['physical_quantity'],
                item['discrepancy'],
                item['discrepancy_value'],
                item['status'],
                item['id']
            ))
            
        except Exception as e:
            print(f"Error updating audit item: {e}")
    
    def update_summary(self):
        total_items = len(self.audit_items)
        items_with_discrepancy = sum(1 for i in self.audit_items if i['discrepancy'] != 0)
        total_discrepancy_value = sum(i['discrepancy_value'] for i in self.audit_items)
        
        self.total_items_label.setText(str(total_items))
        self.discrepancy_count_label.setText(str(items_with_discrepancy))
        self.discrepancy_value_label.setText(format_currency(abs(total_discrepancy_value)))
        
        # Update progress if audit in progress
        if self.current_audit and self.current_audit['status'] == 'in_progress':
            verified_items = sum(1 for i in self.audit_items if i['status'] == 'verified')
            progress = (verified_items / total_items * 100) if total_items > 0 else 0
            self.progress_bar.setValue(int(progress))
    
    def save_audit_progress(self):
        if not self.current_audit:
            return
        
        try:
            # Update audit header
            total_discrepancies = sum(1 for i in self.audit_items if i['discrepancy'] != 0)
            total_discrepancy_value = sum(i['discrepancy_value'] for i in self.audit_items)
            
            query = """
                UPDATE stock_audits 
                SET total_items_audited = %s,
                    total_discrepancies = %s,
                    total_value_discrepancy = %s,
                    notes = %s
                WHERE id = %s
            """
            self.db.execute_query(query, (
                len(self.audit_items),
                total_discrepancies,
                abs(total_discrepancy_value),
                self.audit_notes.toPlainText(),
                self.current_audit['id']
            ))
            
            QMessageBox.information(self, "Success", "Audit progress saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save audit: {str(e)}")
    
    def complete_audit(self):
        if not self.current_audit:
            return
        
        # Verify all items are verified or ask to verify
        pending_items = [i for i in self.audit_items if i['status'] == 'pending']
        if pending_items:
            reply = QMessageBox.question(self, "Pending Items", 
                                        f"There are {len(pending_items)} items pending verification. "
                                        "Mark them as verified and complete?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Mark all as verified
                for item in self.audit_items:
                    item['status'] = 'verified'
        
        try:
            # Update audit status
            total_discrepancies = sum(1 for i in self.audit_items if i['discrepancy'] != 0)
            total_discrepancy_value = sum(i['discrepancy_value'] for i in self.audit_items)
            
            query = """
                UPDATE stock_audits 
                SET status = 'completed',
                    completed_at = NOW(),
                    total_items_audited = %s,
                    total_discrepancies = %s,
                    total_value_discrepancy = %s,
                    notes = %s
                WHERE id = %s
            """
            self.db.execute_query(query, (
                len(self.audit_items),
                total_discrepancies,
                abs(total_discrepancy_value),
                self.audit_notes.toPlainText(),
                self.current_audit['id']
            ))
            
            # Update each item status
            for item in self.audit_items:
                if 'id' in item:
                    item_query = """
                        UPDATE stock_audit_items 
                        SET status = 'verified'
                        WHERE id = %s
                    """
                    self.db.execute_query(item_query, (item['id'],))
            
            # Ask if want to adjust stock based on discrepancies
            if total_discrepancies > 0:
                reply = QMessageBox.question(self, "Adjust Stock", 
                                            "Found discrepancies. Do you want to adjust stock quantities?",
                                            QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    for item in self.audit_items:
                        if item['discrepancy'] != 0:
                            # Update product quantity
                            update_query = """
                                UPDATE products 
                                SET quantity = %s 
                                WHERE id = %s
                            """
                            self.db.execute_query(update_query, 
                                                (item['physical_quantity'], item['product_id']))
            
            self.audit_status_label.setText("Completed")
            self.audit_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            self.start_audit_btn.setEnabled(False)
            self.save_audit_btn.setEnabled(False)
            self.complete_audit_btn.setEnabled(False)
            
            QMessageBox.information(self, "Success", "Audit completed successfully!")
            self.load_audits()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to complete audit: {str(e)}")
    
    def search_products(self):
        search = self.product_search.text()
        category = self.category_filter.currentText()
        
        # This would populate a dropdown or table with search results
        pass


class ProductAuditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.selected_product = None
        self.init_ui()
        self.load_products()
        self.load_categories()
    
    def init_ui(self):
        self.setWindowTitle("Select Product for Audit")
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
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Barcode", "Product", "Current Stock", "Category"])
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
            
            stock_item = QTableWidgetItem(str(product['quantity']))
            if product['quantity'] <= product['reorder_level']:
                stock_item.setForeground(QColor('#F44336'))
            self.products_table.setItem(i, 2, stock_item)
            
            self.products_table.setItem(i, 3, QTableWidgetItem(product['category'] or '-'))
    
    def select_product(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        query = "SELECT * FROM products WHERE barcode = %s"
        self.selected_product = self.db.fetch_one(query, (barcode,))
        self.accept()
    
    def get_selected_product(self):
        return self.selected_product


class StockPickingModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        self.load_pickings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📦 Stock Picking & Order Fulfillment")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Picking list
        left_panel = self.create_picking_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Picking details
        right_panel = self.create_picking_details_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
    
    def create_picking_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.picking_status_filter = QComboBox()
        self.picking_status_filter.addItems(['All', 'pending', 'in_progress', 'completed'])
        self.picking_status_filter.currentTextChanged.connect(self.load_pickings)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.picking_status_filter)
        
        self.picking_search = QLineEdit()
        self.picking_search.setPlaceholderText("Search picking #...")
        self.picking_search.textChanged.connect(self.load_pickings)
        filter_layout.addWidget(self.picking_search)
        
        layout.addLayout(filter_layout)
        
        # Pickings table
        self.pickings_table = QTableWidget()
        self.pickings_table.setColumnCount(6)
        self.pickings_table.setHorizontalHeaderLabels([
            "Picking #", "Type", "Reference", "Items", "Picked", "Status"
        ])
        self.pickings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.pickings_table)
        
        return panel
    
    def create_picking_details_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Picking header
        header_group = QGroupBox("Picking Details")
        header_layout = QGridLayout()
        
        header_layout.addWidget(QLabel("Picking #:"), 0, 0)
        self.picking_number_label = QLabel("-")
        header_layout.addWidget(self.picking_number_label, 0, 1)
        
        header_layout.addWidget(QLabel("Type:"), 0, 2)
        self.picking_type_label = QLabel("-")
        header_layout.addWidget(self.picking_type_label, 0, 3)
        
        header_layout.addWidget(QLabel("Status:"), 1, 0)
        self.picking_status_label = QLabel("-")
        header_layout.addWidget(self.picking_status_label, 1, 1)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items to pick
        items_group = QGroupBox("Items to Pick")
        items_layout = QVBoxLayout()
        
        self.picking_items_table = QTableWidget()
        self.picking_items_table.setColumnCount(5)
        self.picking_items_table.setHorizontalHeaderLabels([
            "Product", "Required", "Picked", "Location", "Status"
        ])
        self.picking_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.picking_items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        
        self.start_picking_btn = QPushButton("▶️ Start Picking")
        actions_layout.addWidget(self.start_picking_btn)
        
        self.complete_picking_btn = QPushButton("✅ Complete Picking")
        actions_layout.addWidget(self.complete_picking_btn)
        
        actions_layout.addStretch()
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        return panel
    
    def load_pickings(self):
        # Implementation for loading pickings
        pass

