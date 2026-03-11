from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QLineEdit,
                           QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox,
                           QDateEdit, QMessageBox, QDialog, QFormLayout,
                           QTabWidget, QSplitter, QFrame, QToolBar)
from PyQt5.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency, validate_barcode, calculate_profit_margin
from datetime import datetime

class ProductsModule(QWidget):
    product_updated = pyqtSignal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.current_product = None
        self.init_ui()
        self.load_products()
        self.load_categories()
        self.load_suppliers()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with search and actions
        header = self.create_header()
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Products list
        left_panel = self.create_product_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Product details
        right_panel = self.create_product_details_panel()
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
        title = QLabel("📦 Product Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2196F3;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search by name, barcode, category...")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.load_products)
        layout.addWidget(self.search_box)
        
        # Add product button
        add_btn = QPushButton("➕ New Product")
        add_btn.clicked.connect(self.new_product)
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
    
    def create_product_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.load_products)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "Barcode", "Product Name", "Category", "Price", "Stock", "Status", "Actions"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemClicked.connect(self.on_product_selected)
        layout.addWidget(self.products_table)
        
        return panel
    
    def create_product_details_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Product form
        form_group = QGroupBox("Product Details")
        form_layout = QGridLayout()
        
        # Row 1
        form_layout.addWidget(QLabel("Barcode:*"), 0, 0)
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan or enter barcode")
        form_layout.addWidget(self.barcode_input, 0, 1)
        
        form_layout.addWidget(QLabel("Product Name:*"), 0, 2)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        form_layout.addWidget(self.name_input, 0, 3)
        
        # Row 2
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        form_layout.addWidget(self.category_combo, 1, 1)
        
        form_layout.addWidget(QLabel("Supplier:"), 1, 2)
        self.supplier_combo = QComboBox()
        form_layout.addWidget(self.supplier_combo, 1, 3)
        
        # Row 3
        form_layout.addWidget(QLabel("Cost Price:"), 2, 0)
        self.cost_price = QDoubleSpinBox()
        self.cost_price.setRange(0, 999999)
        self.cost_price.setPrefix("₹ ")
        self.cost_price.setSingleStep(1)
        form_layout.addWidget(self.cost_price, 2, 1)
        
        form_layout.addWidget(QLabel("Selling Price:*"), 2, 2)
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 999999)
        self.selling_price.setPrefix("₹ ")
        self.selling_price.setSingleStep(1)
        form_layout.addWidget(self.selling_price, 2, 3)
        
        # Row 4
        form_layout.addWidget(QLabel("Current Stock:"), 3, 0)
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        self.stock_input.setSingleStep(1)
        form_layout.addWidget(self.stock_input, 3, 1)
        
        form_layout.addWidget(QLabel("Reorder Level:"), 3, 2)
        self.reorder_level = QSpinBox()
        self.reorder_level.setRange(0, 9999)
        self.reorder_level.setValue(10)
        form_layout.addWidget(self.reorder_level, 3, 3)
        
        # Row 5
        form_layout.addWidget(QLabel("Expiry Date:"), 4, 0)
        self.expiry_date = QDateEdit()
        self.expiry_date.setDate(QDate.currentDate().addMonths(6))
        self.expiry_date.setCalendarPopup(True)
        form_layout.addWidget(self.expiry_date, 4, 1)
        
        form_layout.addWidget(QLabel("Unit:"), 4, 2)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Piece", "Kg", "Liter", "Packet", "Box", "Dozen", "Other"])
        form_layout.addWidget(self.unit_combo, 4, 3)
        
        # Row 6 - Description
        form_layout.addWidget(QLabel("Description:"), 5, 0)
        self.description = QTextEdit()
        self.description.setMaximumHeight(60)
        form_layout.addWidget(self.description, 5, 1, 1, 3)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Margin info
        margin_group = QGroupBox("Profit Margin")
        margin_layout = QHBoxLayout()
        
        self.margin_label = QLabel("0%")
        self.margin_label.setFont(QFont("Arial", 14, QFont.Bold))
        margin_layout.addWidget(self.margin_label)
        
        self.profit_label = QLabel("₹ 0.00")
        self.profit_label.setFont(QFont("Arial", 12))
        margin_layout.addWidget(self.profit_label)
        
        margin_layout.addStretch()
        margin_group.setLayout(margin_layout)
        layout.addWidget(margin_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Product")
        self.save_btn.clicked.connect(self.save_product)
        self.save_btn.setStyleSheet("background-color: #2196F3;")
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_product)
        self.delete_btn.setStyleSheet("background-color: #F44336;")
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("🔄 Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Connect price changes to update margin
        self.cost_price.valueChanged.connect(self.update_margin)
        self.selling_price.valueChanged.connect(self.update_margin)
        
        return panel
    
    def load_categories(self):
        try:
            query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''"
            categories = self.db.fetch_all(query)
            
            self.category_combo.clear()
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            self.category_combo.addItem("")  # Empty option
            
            for cat in categories:
                if cat['category']:
                    self.category_combo.addItem(cat['category'])
                    self.category_filter.addItem(cat['category'])
                    
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def load_suppliers(self):
        try:
            query = "SELECT id, name FROM suppliers WHERE status = 'active'"
            suppliers = self.db.fetch_all(query)
            
            self.supplier_combo.clear()
            self.supplier_combo.addItem("None", None)
            
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier['name'], supplier['id'])
                
        except Exception as e:
            print(f"Error loading suppliers: {e}")
    
    def load_products(self):
        try:
            search = self.search_box.text()
            category = self.category_filter.currentText()
            
            query = """
                SELECT p.*, s.name as supplier_name 
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (p.name LIKE %s OR p.barcode LIKE %s OR p.category LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            if category and category != "All Categories":
                query += " AND p.category = %s"
                params.append(category)
            
            query += " ORDER BY p.name"
            
            products = self.db.fetch_all(query, params)
            
            self.products_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.products_table.setItem(i, 0, QTableWidgetItem(product['barcode'] or ''))
                self.products_table.setItem(i, 1, QTableWidgetItem(product['name']))
                self.products_table.setItem(i, 2, QTableWidgetItem(product['category'] or '-'))
                self.products_table.setItem(i, 3, QTableWidgetItem(format_currency(product['selling_price'])))
                
                # Stock with color coding
                stock_item = QTableWidgetItem(str(product['quantity']))
                if product['quantity'] <= product['reorder_level']:
                    stock_item.setForeground(QColor('#F44336'))
                    stock_item.setBackground(QColor('#FFEBEE'))
                self.products_table.setItem(i, 4, stock_item)
                
                # Status
                if product['quantity'] <= 0:
                    status = "Out of Stock"
                    color = '#F44336'
                elif product['quantity'] <= product['reorder_level']:
                    status = "Low Stock"
                    color = '#FF9800'
                else:
                    status = "In Stock"
                    color = '#4CAF50'
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(color))
                self.products_table.setItem(i, 5, status_item)
                
                # Edit button
                edit_btn = QPushButton("✏️ Edit")
                edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
                self.products_table.setCellWidget(i, 6, edit_btn)
                
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def on_product_selected(self, item):
        row = item.row()
        barcode = self.products_table.item(row, 0).text()
        self.load_product(barcode)
    
    def load_product(self, barcode):
        try:
            query = "SELECT * FROM products WHERE barcode = %s"
            product = self.db.fetch_one(query, (barcode,))
            
            if product:
                self.current_product = product
                self.barcode_input.setText(product['barcode'] or '')
                self.name_input.setText(product['name'] or '')
                
                # Set category
                index = self.category_combo.findText(product['category'] or '')
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                else:
                    self.category_combo.setEditText(product['category'] or '')
                
                # Set supplier
                if product['supplier_id']:
                    index = self.supplier_combo.findData(product['supplier_id'])
                    if index >= 0:
                        self.supplier_combo.setCurrentIndex(index)
                    else:
                        self.supplier_combo.setCurrentIndex(0)
                else:
                    self.supplier_combo.setCurrentIndex(0)
                
                self.cost_price.setValue(float(product['cost_price'] or 0))
                self.selling_price.setValue(float(product['selling_price'] or 0))
                self.stock_input.setValue(product['quantity'] or 0)
                self.reorder_level.setValue(product['reorder_level'] or 10)
                
                if product['expiry_date']:
                    try:
                        if isinstance(product['expiry_date'], str):
                            date_obj = datetime.strptime(product['expiry_date'], '%Y-%m-%d').date()
                        else:
                            date_obj = product['expiry_date']
                        self.expiry_date.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                    except:
                        self.expiry_date.setDate(QDate.currentDate().addMonths(6))
                else:
                    self.expiry_date.setDate(QDate.currentDate().addMonths(6))
                
                # Handle description field
                try:
                    self.description.setText(product.get('description', '') or '')
                except:
                    self.description.setText('')
                
                self.delete_btn.setEnabled(True)
                self.update_margin()
                
        except Exception as e:
            print(f"Error loading product: {e}")
            QMessageBox.warning(self, "Error", f"Could not load product: {str(e)}")
    
    def new_product(self):
        self.current_product = None
        self.clear_form()
        self.delete_btn.setEnabled(False)
        self.barcode_input.setFocus()
    
    def clear_form(self):
        self.barcode_input.clear()
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.supplier_combo.setCurrentIndex(0)
        self.cost_price.setValue(0)
        self.selling_price.setValue(0)
        self.stock_input.setValue(0)
        self.reorder_level.setValue(10)
        self.expiry_date.setDate(QDate.currentDate().addMonths(6))
        self.description.clear()
        self.update_margin()
    
    def update_margin(self):
        cost = self.cost_price.value()
        selling = self.selling_price.value()
        
        if cost > 0:
            margin_percent = ((selling - cost) / cost) * 100
            profit = selling - cost
            self.margin_label.setText(f"{margin_percent:.1f}%")
            self.profit_label.setText(format_currency(profit))
            
            # Color code margin
            if margin_percent < 10:
                self.margin_label.setStyleSheet("color: #F44336;")
            elif margin_percent < 20:
                self.margin_label.setStyleSheet("color: #FF9800;")
            else:
                self.margin_label.setStyleSheet("color: #4CAF50;")
        else:
            self.margin_label.setText("N/A")
            self.profit_label.setText("₹ 0.00")
            self.margin_label.setStyleSheet("color: gray;")
    
    def save_product(self):
        # Validate
        if not self.barcode_input.text():
            QMessageBox.warning(self, "Validation", "Barcode is required.")
            return
        
        if not validate_barcode(self.barcode_input.text()):
            reply = QMessageBox.question(self, "Invalid Barcode", 
                                       "Barcode format may be invalid. Save anyway?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        if not self.name_input.text():
            QMessageBox.warning(self, "Validation", "Product name is required.")
            return
        
        if self.selling_price.value() <= 0:
            QMessageBox.warning(self, "Validation", "Selling price must be greater than 0.")
            return
        
        try:
            if self.current_product:
                # Update existing product
                query = """
                    UPDATE products 
                    SET barcode = %s, name = %s, category = %s, supplier_id = %s,
                        cost_price = %s, selling_price = %s, quantity = %s,
                        reorder_level = %s, expiry_date = %s, description = %s
                    WHERE id = %s
                """
                self.db.execute_query(query, (
                    self.barcode_input.text(),
                    self.name_input.text(),
                    self.category_combo.currentText() or None,
                    self.supplier_combo.currentData(),
                    self.cost_price.value(),
                    self.selling_price.value(),
                    self.stock_input.value(),
                    self.reorder_level.value(),
                    self.expiry_date.date().toString('yyyy-MM-dd') if self.expiry_date.date() > QDate.currentDate() else None,
                    self.description.toPlainText() or None,
                    self.current_product['id']
                ))
                
                QMessageBox.information(self, "Success", "Product updated successfully!")
                
            else:
                # Check if barcode exists
                check_query = "SELECT id FROM products WHERE barcode = %s"
                existing = self.db.fetch_one(check_query, (self.barcode_input.text(),))
                if existing:
                    QMessageBox.warning(self, "Duplicate", "Barcode already exists!")
                    return
                
                # Insert new product
                query = """
                    INSERT INTO products 
                    (barcode, name, category, supplier_id, cost_price, selling_price, 
                     quantity, reorder_level, expiry_date, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_query(query, (
                    self.barcode_input.text(),
                    self.name_input.text(),
                    self.category_combo.currentText() or None,
                    self.supplier_combo.currentData(),
                    self.cost_price.value(),
                    self.selling_price.value(),
                    self.stock_input.value(),
                    self.reorder_level.value(),
                    self.expiry_date.date().toString('yyyy-MM-dd') if self.expiry_date.date() > QDate.currentDate() else None,
                    self.description.toPlainText() or None
                ))
                
                QMessageBox.information(self, "Success", "Product added successfully!")
            
            # Refresh
            self.load_products()
            self.load_categories()
            self.product_updated.emit()
            self.new_product()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
    
    def delete_product(self):
        if not self.current_product:
            return
        
        reply = QMessageBox.question(self, "Delete Product", 
                                    f"Are you sure you want to delete {self.current_product['name']}?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM products WHERE id = %s"
                self.db.execute_query(query, (self.current_product['id'],))
                
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products()
                self.new_product()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
    
    def edit_product(self, product):
        self.load_product(product['barcode'])
