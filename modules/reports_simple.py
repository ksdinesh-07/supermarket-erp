from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QComboBox,
                           QDateEdit, QMessageBox, QTabWidget, QFrame,
                           QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from datetime import datetime
import csv

class ReportsModule(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        self.load_dashboard()
        self.load_categories()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📊 Reports & Analytics")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget for different reports
        self.tab_widget = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(dashboard_tab, "📈 Dashboard")
        
        # Sales report tab
        sales_tab = self.create_sales_report_tab()
        self.tab_widget.addTab(sales_tab, "💰 Sales Report")
        
        # Inventory report tab
        inventory_tab = self.create_inventory_report_tab()
        self.tab_widget.addTab(inventory_tab, "📦 Inventory Report")
        
        # Customer report tab
        customer_tab = self.create_customer_report_tab()
        self.tab_widget.addTab(customer_tab, "👥 Customer Report")
        
        # Product performance tab
        product_tab = self.create_product_report_tab()
        self.tab_widget.addTab(product_tab, "📊 Product Performance")
        
        # Financial report tab
        financial_tab = self.create_financial_report_tab()
        self.tab_widget.addTab(financial_tab, "💰 Financial Report")
        
        layout.addWidget(self.tab_widget)
        
    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Key metrics in a grid
        metrics_layout = QGridLayout()
        
        # Today's sales
        self.today_sales_card = self.create_metric_card("Today's Sales", "₹ 0", "💰")
        metrics_layout.addWidget(self.today_sales_card, 0, 0)
        
        # Weekly sales
        self.weekly_sales_card = self.create_metric_card("This Week", "₹ 0", "📊")
        metrics_layout.addWidget(self.weekly_sales_card, 0, 1)
        
        # Monthly sales
        self.monthly_sales_card = self.create_metric_card("This Month", "₹ 0", "📈")
        metrics_layout.addWidget(self.monthly_sales_card, 0, 2)
        
        # Total products
        self.total_products_card = self.create_metric_card("Total Products", "0", "📦")
        metrics_layout.addWidget(self.total_products_card, 1, 0)
        
        # Total customers
        self.total_customers_card = self.create_metric_card("Total Customers", "0", "👥")
        metrics_layout.addWidget(self.total_customers_card, 1, 1)
        
        # Low stock
        self.low_stock_card = self.create_metric_card("Low Stock", "0", "⚠️")
        metrics_layout.addWidget(self.low_stock_card, 1, 2)
        
        layout.addLayout(metrics_layout)
        
        # Top products
        top_group = QGroupBox("Top Selling Products")
        top_layout = QVBoxLayout()
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(3)
        self.top_products_table.setHorizontalHeaderLabels(["Product", "Quantity", "Revenue"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        top_layout.addWidget(self.top_products_table)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Activity", "Details"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        activity_layout.addWidget(self.activity_table)
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        return tab
    
    def create_metric_card(self, title, value, icon):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #ddd;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 20))
        title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: gray;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(value_label)
        
        return card
    
    def create_sales_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Date Range:"), 0, 0)
        self.sales_date_from = QDateEdit()
        self.sales_date_from.setDate(QDate.currentDate().addDays(-30))
        self.sales_date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.sales_date_from, 0, 1)
        
        filter_layout.addWidget(QLabel("to"), 0, 2)
        self.sales_date_to = QDateEdit()
        self.sales_date_to.setDate(QDate.currentDate())
        self.sales_date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.sales_date_to, 0, 3)
        
        self.generate_sales_btn = QPushButton("📊 Generate Report")
        self.generate_sales_btn.clicked.connect(self.generate_sales_report)
        filter_layout.addWidget(self.generate_sales_btn, 1, 0, 1, 4)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        
        self.total_sales_label = QLabel("Total Sales: ₹ 0")
        self.total_sales_label.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(self.total_sales_label)
        
        self.total_transactions_label = QLabel("Transactions: 0")
        summary_layout.addWidget(self.total_transactions_label)
        
        summary_layout.addStretch()
        
        export_btn = QPushButton("📥 Export CSV")
        export_btn.clicked.connect(self.export_sales_csv)
        summary_layout.addWidget(export_btn)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Sales table
        self.sales_report_table = QTableWidget()
        self.sales_report_table.setColumnCount(6)
        self.sales_report_table.setHorizontalHeaderLabels([
            "Date", "Invoice #", "Customer", "Payment", "Amount", "Cashier"
        ])
        self.sales_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.sales_report_table)
        
        return tab
    
    def create_inventory_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "Product", "Category", "Stock", "Selling Price", "Margin", "Status"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.inventory_table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Inventory Report")
        refresh_btn.clicked.connect(self.load_inventory_report)
        layout.addWidget(refresh_btn)
        
        return tab
    
    def create_customer_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Top customers
        top_group = QGroupBox("Top Customers by Spending")
        top_layout = QVBoxLayout()
        
        self.top_customers_table = QTableWidget()
        self.top_customers_table.setColumnCount(4)
        self.top_customers_table.setHorizontalHeaderLabels(["Customer", "Phone", "Total Spent", "Orders"])
        self.top_customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        top_layout.addWidget(self.top_customers_table)
        
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Customer Report")
        refresh_btn.clicked.connect(self.load_customer_report)
        layout.addWidget(refresh_btn)
        
        return tab
    
    def create_product_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Category:"))
        self.product_category_filter = QComboBox()
        self.product_category_filter.addItem("All Categories")
        filter_layout.addWidget(self.product_category_filter)
        
        self.generate_product_btn = QPushButton("Generate")
        self.generate_product_btn.clicked.connect(self.load_product_performance)
        filter_layout.addWidget(self.generate_product_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Product performance table
        self.product_performance_table = QTableWidget()
        self.product_performance_table.setColumnCount(5)
        self.product_performance_table.setHorizontalHeaderLabels([
            "Product", "Category", "Sold", "Revenue", "Stock Status"
        ])
        self.product_performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.product_performance_table)
        
        return tab
    
    def create_financial_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Monthly breakdown
        monthly_group = QGroupBox("Monthly Breakdown")
        monthly_layout = QVBoxLayout()
        
        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(3)
        self.monthly_table.setHorizontalHeaderLabels(["Month", "Revenue", "Profit"])
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        monthly_layout.addWidget(self.monthly_table)
        
        monthly_group.setLayout(monthly_layout)
        layout.addWidget(monthly_group)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Financial Report")
        refresh_btn.clicked.connect(self.load_financial_report)
        layout.addWidget(refresh_btn)
        
        return tab
    
    def load_categories(self):
        try:
            query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL"
            categories = self.db.fetch_all(query)
            for cat in categories:
                if cat['category']:
                    self.product_category_filter.addItem(cat['category'])
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def load_dashboard(self):
        try:
            # Today's sales
            today_query = "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE DATE(created_at) = CURDATE()"
            today_result = self.db.fetch_one(today_query)
            today_sales = today_result['total'] if today_result else 0
            
            # Weekly sales
            week_query = "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            week_result = self.db.fetch_one(week_query)
            week_sales = week_result['total'] if week_result else 0
            
            # Monthly sales
            month_query = "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
            month_result = self.db.fetch_one(month_query)
            month_sales = month_result['total'] if month_result else 0
            
            # Update cards
            self.today_sales_card.findChild(QLabel, "value_label").setText(format_currency(today_sales))
            self.weekly_sales_card.findChild(QLabel, "value_label").setText(format_currency(week_sales))
            self.monthly_sales_card.findChild(QLabel, "value_label").setText(format_currency(month_sales))
            
            # Product count
            product_query = "SELECT COUNT(*) as count FROM products"
            product_result = self.db.fetch_one(product_query)
            self.total_products_card.findChild(QLabel, "value_label").setText(str(product_result['count']))
            
            # Customer count
            customer_query = "SELECT COUNT(*) as count FROM customers"
            customer_result = self.db.fetch_one(customer_query)
            self.total_customers_card.findChild(QLabel, "value_label").setText(str(customer_result['count']))
            
            # Low stock
            low_stock_query = "SELECT COUNT(*) as count FROM products WHERE quantity <= reorder_level"
            low_stock_result = self.db.fetch_one(low_stock_query)
            self.low_stock_card.findChild(QLabel, "value_label").setText(str(low_stock_result['count']))
            
            # Top products
            self.load_top_products()
            
            # Recent activity
            self.load_recent_activity()
            
        except Exception as e:
            print(f"Error loading dashboard: {e}")
    
    def load_top_products(self):
        try:
            query = """
                SELECT p.name, COALESCE(SUM(si.quantity), 0) as total_qty, 
                       COALESCE(SUM(si.subtotal), 0) as total_revenue
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                GROUP BY p.id
                ORDER BY total_revenue DESC
                LIMIT 5
            """
            products = self.db.fetch_all(query)
            
            self.top_products_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.top_products_table.setItem(i, 0, QTableWidgetItem(product['name']))
                self.top_products_table.setItem(i, 1, QTableWidgetItem(str(product['total_qty'])))
                self.top_products_table.setItem(i, 2, QTableWidgetItem(format_currency(product['total_revenue'])))
                
        except Exception as e:
            print(f"Error loading top products: {e}")
    
    def load_recent_activity(self):
        try:
            # Get recent sales
            query = """
                SELECT s.created_at, s.invoice_number, s.total_amount, u.username
                FROM sales s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
                LIMIT 5
            """
            activities = self.db.fetch_all(query)
            
            self.activity_table.setRowCount(len(activities))
            for i, activity in enumerate(activities):
                if isinstance(activity['created_at'], datetime):
                    time_str = activity['created_at'].strftime('%H:%M %d/%m')
                else:
                    time_str = str(activity['created_at'])
                self.activity_table.setItem(i, 0, QTableWidgetItem(time_str))
                self.activity_table.setItem(i, 1, QTableWidgetItem(f"Sale #{activity['invoice_number']}"))
                self.activity_table.setItem(i, 2, QTableWidgetItem(f"{format_currency(activity['total_amount'])} by {activity['username']}"))
                
        except Exception as e:
            print(f"Error loading activities: {e}")
    
    def generate_sales_report(self):
        try:
            date_from = self.sales_date_from.date().toString('yyyy-MM-dd')
            date_to = self.sales_date_to.date().toString('yyyy-MM-dd')
            
            query = """
                SELECT s.*, u.username as cashier_name, c.name as customer_name
                FROM sales s
                LEFT JOIN users u ON s.user_id = u.id
                LEFT JOIN customers c ON s.customer_id = c.id
                WHERE DATE(s.created_at) BETWEEN %s AND %s
                ORDER BY s.created_at DESC
            """
            params = [date_from, date_to]
            
            sales = self.db.fetch_all(query, params)
            
            # Update table
            self.sales_report_table.setRowCount(len(sales))
            total_amount = 0
            
            for i, sale in enumerate(sales):
                if isinstance(sale['created_at'], datetime):
                    date_str = sale['created_at'].strftime('%d/%m/%Y %H:%M')
                else:
                    date_str = str(sale['created_at'])
                self.sales_report_table.setItem(i, 0, QTableWidgetItem(date_str))
                self.sales_report_table.setItem(i, 1, QTableWidgetItem(sale['invoice_number']))
                self.sales_report_table.setItem(i, 2, QTableWidgetItem(sale.get('customer_name', 'Walk-in') or 'Walk-in'))
                self.sales_report_table.setItem(i, 3, QTableWidgetItem(sale.get('payment_method', 'cash').upper()))
                self.sales_report_table.setItem(i, 4, QTableWidgetItem(format_currency(sale['total_amount'])))
                self.sales_report_table.setItem(i, 5, QTableWidgetItem(sale.get('cashier_name', '-')))
                
                total_amount += sale['total_amount']
            
            # Update summary
            self.total_sales_label.setText(f"Total Sales: {format_currency(total_amount)}")
            self.total_transactions_label.setText(f"Transactions: {len(sales)}")
            
        except Exception as e:
            print(f"Error generating sales report: {e}")
    
    def load_inventory_report(self):
        try:
            query = """
                SELECT *, 
                       CASE 
                           WHEN cost_price > 0 THEN ((selling_price - cost_price) / cost_price * 100)
                           ELSE 0
                       END as margin_percent
                FROM products
                ORDER BY name
            """
            products = self.db.fetch_all(query)
            
            self.inventory_table.setRowCount(len(products))
            
            for i, product in enumerate(products):
                self.inventory_table.setItem(i, 0, QTableWidgetItem(product['name']))
                self.inventory_table.setItem(i, 1, QTableWidgetItem(product['category'] or '-'))
                self.inventory_table.setItem(i, 2, QTableWidgetItem(str(product['quantity'])))
                self.inventory_table.setItem(i, 3, QTableWidgetItem(format_currency(product['selling_price'])))
                
                margin = float(product.get('margin_percent', 0))
                margin_item = QTableWidgetItem(f"{margin:.1f}%")
                if margin < 10:
                    margin_item.setForeground(QColor('#F44336'))
                elif margin < 20:
                    margin_item.setForeground(QColor('#FF9800'))
                else:
                    margin_item.setForeground(QColor('#4CAF50'))
                self.inventory_table.setItem(i, 4, margin_item)
                
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
                self.inventory_table.setItem(i, 5, status_item)
                
        except Exception as e:
            print(f"Error loading inventory report: {e}")
    
    def load_customer_report(self):
        try:
            # Top customers
            query = """
                SELECT c.name, c.phone, 
                       COUNT(s.id) as order_count,
                       COALESCE(SUM(s.total_amount), 0) as total_spent
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                GROUP BY c.id
                ORDER BY total_spent DESC
                LIMIT 10
            """
            customers = self.db.fetch_all(query)
            
            self.top_customers_table.setRowCount(len(customers))
            for i, customer in enumerate(customers):
                self.top_customers_table.setItem(i, 0, QTableWidgetItem(customer['name']))
                self.top_customers_table.setItem(i, 1, QTableWidgetItem(customer['phone']))
                self.top_customers_table.setItem(i, 2, QTableWidgetItem(format_currency(customer['total_spent'])))
                self.top_customers_table.setItem(i, 3, QTableWidgetItem(str(customer['order_count'])))
                
        except Exception as e:
            print(f"Error loading customer report: {e}")
    
    def load_product_performance(self):
        try:
            category = self.product_category_filter.currentText()
            
            query = """
                SELECT p.name, p.category,
                       COALESCE(SUM(si.quantity), 0) as total_sold,
                       COALESCE(SUM(si.subtotal), 0) as total_revenue,
                       p.quantity as current_stock,
                       p.reorder_level
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                WHERE 1=1
            """
            params = []
            
            if category != "All Categories":
                query += " AND p.category = %s"
                params.append(category)
            
            query += " GROUP BY p.id ORDER BY total_revenue DESC"
            
            products = self.db.fetch_all(query, params)
            
            self.product_performance_table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.product_performance_table.setItem(i, 0, QTableWidgetItem(product['name']))
                self.product_performance_table.setItem(i, 1, QTableWidgetItem(product['category'] or '-'))
                self.product_performance_table.setItem(i, 2, QTableWidgetItem(str(product['total_sold'])))
                self.product_performance_table.setItem(i, 3, QTableWidgetItem(format_currency(product['total_revenue'])))
                
                # Stock status
                if product['current_stock'] <= 0:
                    status = "Out of Stock"
                    color = '#F44336'
                elif product['current_stock'] <= product['reorder_level']:
                    status = "Low Stock"
                    color = '#FF9800'
                else:
                    status = "In Stock"
                    color = '#4CAF50'
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(color))
                self.product_performance_table.setItem(i, 4, status_item)
                
        except Exception as e:
            print(f"Error loading product performance: {e}")
    
    def load_financial_report(self):
        try:
            # Monthly breakdown
            monthly_query = """
                SELECT 
                    DATE_FORMAT(s.created_at, '%Y-%m') as month,
                    COALESCE(SUM(s.total_amount), 0) as revenue,
                    COALESCE(SUM(s.total_amount - (si.quantity * p.cost_price)), 0) as profit
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                LEFT JOIN products p ON si.product_id = p.id
                GROUP BY DATE_FORMAT(s.created_at, '%Y-%m')
                ORDER BY month DESC
                LIMIT 6
            """
            monthly = self.db.fetch_all(monthly_query)
            
            self.monthly_table.setRowCount(len(monthly))
            for i, month in enumerate(monthly):
                self.monthly_table.setItem(i, 0, QTableWidgetItem(month['month']))
                self.monthly_table.setItem(i, 1, QTableWidgetItem(format_currency(month['revenue'])))
                
                profit_item = QTableWidgetItem(format_currency(month['profit']))
                if month['profit'] > 0:
                    profit_item.setForeground(QColor('#4CAF50'))
                else:
                    profit_item.setForeground(QColor('#F44336'))
                self.monthly_table.setItem(i, 2, profit_item)
                
        except Exception as e:
            print(f"Error loading financial report: {e}")
    
    def export_sales_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Sales Report", "", "CSV Files (*.csv)")
            if filename:
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    # Write header
                    writer.writerow(["Date", "Invoice #", "Customer", "Payment", "Amount", "Cashier"])
                    
                    # Write data
                    for row in range(self.sales_report_table.rowCount()):
                        date = self.sales_report_table.item(row, 0).text()
                        invoice = self.sales_report_table.item(row, 1).text()
                        customer = self.sales_report_table.item(row, 2).text()
                        payment = self.sales_report_table.item(row, 3).text()
                        amount = self.sales_report_table.item(row, 4).text()
                        cashier = self.sales_report_table.item(row, 5).text()
                        
                        writer.writerow([date, invoice, customer, payment, amount, cashier])
                
                QMessageBox.information(self, "Success", f"Report exported to {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
