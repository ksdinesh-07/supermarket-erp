from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QStackedWidget, QFrame,
                           QMessageBox, QStatusBar, QToolBar, QAction,
                           QTabWidget, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QMenu)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from datetime import datetime
from database.models import ProductModel, SaleModel, CustomerModel
from database.connection import DatabaseConnection
from utils.helpers import format_currency, get_current_date
from config import THEME

# Import all modules
from modules.products import ProductsModule
from modules.customers import CustomersModule
from modules.reports import ReportsModule
from modules.admin import AdminModule
from modules.online_ordering.online_orders import OnlineOrderingModule
from modules.kiosk.self_checkout import SelfCheckoutKiosk
from modules.goods_inward.goods_inward import GoodsInwardModule
from modules.alerts.business_alerts import BusinessAlertsModule
from modules.audit.stock_audit import StockAuditModule, StockPickingModule
from modules.purchases.centralized_purchases import CentralizedPurchasesModule
from modules.billing.superfast_billing import SuperfastBillingModule

class MainDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()  # Add this line
        self.product_model = ProductModel()
        self.sale_model = SaleModel()
        self.customer_model = CustomerModel()
        self.summary_cards = {}
        self.init_ui()
        self.load_dashboard_data()
        
        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_dashboard_data)
        self.timer.start(30000)
        
    def init_ui(self):
        self.setWindowTitle(f"Supermarket ERP - Welcome {self.user['full_name']} ({self.user['role']})")
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply stylesheet
        try:
            with open('ui/styles/modern_blue.qss', 'r') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found, using default styles")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget with optimized organization
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        
        # === GROUP 1: CORE OPERATIONS (Always visible) ===
        
        # Dashboard tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Products tab
        self.products_tab = ProductsModule(self.user)
        self.products_tab.product_updated.connect(self.load_dashboard_data)
        self.tab_widget.addTab(self.products_tab, "📦 Products")
        
        # Customers tab
        self.customers_tab = CustomersModule(self.user)
        self.customers_tab.customer_updated.connect(self.load_dashboard_data)
        self.tab_widget.addTab(self.customers_tab, "👥 Customers")
        
        # Billing tab (most frequently used)
        self.billing_tab = SuperfastBillingModule(self.user)
        self.billing_tab.billing_completed.connect(self.on_billing_completed)
        self.tab_widget.addTab(self.billing_tab, "⚡ Billing")
        
        # === GROUP 2: SALES & ORDERS (Combined in one tab with sub-tabs) ===
        self.sales_tab = self.create_sales_dashboard_tab()
        self.tab_widget.addTab(self.sales_tab, "🛒 Sales")
        
        # === GROUP 3: INVENTORY MANAGEMENT (Combined) ===
        self.inventory_tab = self.create_inventory_dashboard_tab()
        self.tab_widget.addTab(self.inventory_tab, "📦 Inventory")
        
        # === GROUP 4: REPORTS & ANALYTICS ===
        self.reports_tab = ReportsModule(self.user)
        self.tab_widget.addTab(self.reports_tab, "📊 Reports")
        
        # === GROUP 5: SYSTEM (Alerts & Admin) ===
        self.alerts_tab = BusinessAlertsModule(self.user)
        self.alerts_tab.alert_clicked.connect(self.handle_alert_click)
        self.tab_widget.addTab(self.alerts_tab, "🔔 Alerts")
        
        # Admin tab (only for admin)
        if self.user['role'] == 'admin':
            self.admin_tab = AdminModule(self.user)
            self.tab_widget.addTab(self.admin_tab, "⚙️ Admin")
        
        # Enable scrolling for safety
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.ElideRight)
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.create_status_bar()
        
    def create_sales_dashboard_tab(self):
        """Create a combined sales tab with sub-tabs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sub-tab widget
        sub_tabs = QTabWidget()
        sub_tabs.setDocumentMode(True)
        
        # POS sub-tab
        self.pos_tab = self.create_pos_tab()
        sub_tabs.addTab(self.pos_tab, "🛒 POS")
        
        # Online Orders sub-tab
        self.online_ordering_tab = OnlineOrderingModule(self.user)
        sub_tabs.addTab(self.online_ordering_tab, "🛵 Online")
        
        # Kiosk sub-tab
        self.kiosk_tab = SelfCheckoutKiosk(self.user)
        sub_tabs.addTab(self.kiosk_tab, "🛍️ Kiosk")
        
        layout.addWidget(sub_tabs)
        return tab
    
    def create_inventory_dashboard_tab(self):
        """Create a combined inventory tab with sub-tabs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sub-tab widget
        sub_tabs = QTabWidget()
        sub_tabs.setDocumentMode(True)
        
        # Goods Inward sub-tab
        self.goods_inward_tab = GoodsInwardModule(self.user)
        sub_tabs.addTab(self.goods_inward_tab, "📥 Goods Inward")
        
        # Stock Audit sub-tab
        self.audit_tab = StockAuditModule(self.user)
        sub_tabs.addTab(self.audit_tab, "🔍 Stock Audit")
        
        # Stock Picking sub-tab
        self.picking_tab = StockPickingModule(self.user)
        sub_tabs.addTab(self.picking_tab, "📦 Stock Picking")
        
        # Purchases sub-tab
        self.purchases_tab = CentralizedPurchasesModule(self.user)
        sub_tabs.addTab(self.purchases_tab, "📋 Purchases")
        
        layout.addWidget(sub_tabs)
        return tab
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu - Quick navigation to all sections
        view_menu = menubar.addMenu('View')
        
        # Core sections
        dashboard_action = QAction('Dashboard', self)
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)
        
        products_action = QAction('Products', self)
        products_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(products_action)
        
        customers_action = QAction('Customers', self)
        customers_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(customers_action)
        
        billing_action = QAction('Billing', self)
        billing_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        view_menu.addAction(billing_action)
        
        # Sales sub-menu
        sales_menu = view_menu.addMenu('Sales')
        
        pos_action = QAction('Point of Sale', self)
        pos_action.triggered.connect(lambda: self.show_sub_tab(4, 0))
        sales_menu.addAction(pos_action)
        
        online_action = QAction('Online Orders', self)
        online_action.triggered.connect(lambda: self.show_sub_tab(4, 1))
        sales_menu.addAction(online_action)
        
        kiosk_action = QAction('Self Checkout', self)
        kiosk_action.triggered.connect(lambda: self.show_sub_tab(4, 2))
        sales_menu.addAction(kiosk_action)
        
        # Inventory sub-menu
        inventory_menu = view_menu.addMenu('Inventory')
        
        inward_action = QAction('Goods Inward', self)
        inward_action.triggered.connect(lambda: self.show_sub_tab(5, 0))
        inventory_menu.addAction(inward_action)
        
        audit_action = QAction('Stock Audit', self)
        audit_action.triggered.connect(lambda: self.show_sub_tab(5, 1))
        inventory_menu.addAction(audit_action)
        
        picking_action = QAction('Stock Picking', self)
        picking_action.triggered.connect(lambda: self.show_sub_tab(5, 2))
        inventory_menu.addAction(picking_action)
        
        purchase_action = QAction('Purchase Orders', self)
        purchase_action.triggered.connect(lambda: self.show_sub_tab(5, 3))
        inventory_menu.addAction(purchase_action)
        
        # Reports
        reports_action = QAction('Reports', self)
        reports_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(6))
        view_menu.addAction(reports_action)
        
        # Alerts
        alerts_action = QAction('Alerts', self)
        alerts_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(7))
        view_menu.addAction(alerts_action)
        
        # Admin (if applicable)
        if self.user['role'] == 'admin':
            admin_action = QAction('Admin', self)
            admin_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(8))
            view_menu.addAction(admin_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_sub_tab(self, main_tab_index, sub_tab_index):
        """Switch to a specific sub-tab"""
        self.tab_widget.setCurrentIndex(main_tab_index)
        main_tab = self.tab_widget.widget(main_tab_index)
        if main_tab:
            # Find the sub-tab widget in the layout
            sub_tabs = main_tab.layout().itemAt(0).widget()
            if isinstance(sub_tabs, QTabWidget):
                sub_tabs.setCurrentIndex(sub_tab_index)
    
    def create_toolbar(self):
        toolbar = QToolBar("Quick Actions")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Most frequently used actions
        actions = [
            ("📊 Dashboard", 0),
            ("📦 Products", 1),
            ("👥 Customers", 2),
            ("⚡ Billing", 3),
            ("🛒 Sales", 4),
            ("📊 Reports", 6),
            ("🔔 Alerts", 7)
        ]
        
        if self.user['role'] == 'admin':
            actions.append(("⚙️ Admin", 8))
        
        for text, index in actions:
            action = QAction(text, self)
            action.triggered.connect(lambda checked, idx=index: self.tab_widget.setCurrentIndex(idx))
            toolbar.addAction(action)
        
        toolbar.addSeparator()
        
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.load_dashboard_data)
        toolbar.addAction(refresh_action)
    
    def create_header(self):
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setMaximumHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        welcome_label = QLabel(f"Welcome, {self.user['full_name']}!")
        welcome_label.setFont(QFont("Arial", 14, QFont.Bold))
        welcome_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(welcome_label)
        
        layout.addStretch()
        
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Arial", 12))
        self.datetime_label.setStyleSheet("color: #666;")
        layout.addWidget(self.datetime_label)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_datetime)
        self.time_timer.start(1000)
        self.update_datetime()
        
        return header
    
    def update_datetime(self):
        now = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        self.datetime_label.setText(now)
    
    def create_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        self.user_status = QLabel(f"👤 {self.user['username']} ({self.user['role']})")
        status_bar.addWidget(self.user_status)
        
        status_bar.addPermanentWidget(QLabel(f"📅 {get_current_date()}"))
        status_bar.addPermanentWidget(QLabel("v1.0.0"))
    
    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        sales_card, sales_value = self.create_summary_card("Today's Sales", "₹ 0", "💰")
        cards_layout.addWidget(sales_card)
        self.summary_cards['sales'] = sales_value
        
        products_card, products_value = self.create_summary_card("Total Products", "0", "📦")
        cards_layout.addWidget(products_card)
        self.summary_cards['products'] = products_value
        
        customers_card, customers_value = self.create_summary_card("Total Customers", "0", "👥")
        cards_layout.addWidget(customers_card)
        self.summary_cards['customers'] = customers_value
        
        pending_card, pending_value = self.create_summary_card("Pending Orders", "0", "🛵")
        cards_layout.addWidget(pending_card)
        self.summary_cards['pending'] = pending_value
        
        layout.addLayout(cards_layout)
        
        # Recent Sales
        recent_sales_group = QGroupBox("Recent Sales")
        recent_sales_layout = QVBoxLayout()
        self.recent_sales_table = QTableWidget()
        self.recent_sales_table.setColumnCount(4)
        self.recent_sales_table.setHorizontalHeaderLabels(["Invoice", "Customer", "Amount", "Time"])
        self.recent_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_sales_layout.addWidget(self.recent_sales_table)
        recent_sales_group.setLayout(recent_sales_layout)
        layout.addWidget(recent_sales_group)
        
        return tab
    
    def create_summary_card(self, title, value, icon):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: gray;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {THEME['primary']};")
        layout.addWidget(value_label)
        
        return card, value_label
    
    def load_dashboard_data(self):
        try:
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            
            # Today's sales
            sales_summary = self.sale_model.get_sales_summary(today, today)
            if sales_summary and sales_summary['total_revenue']:
                self.summary_cards['sales'].setText(format_currency(sales_summary['total_revenue']))
            else:
                self.summary_cards['sales'].setText(format_currency(0))
            
            # Products count
            products = self.product_model.get_all_products()
            self.summary_cards['products'].setText(str(len(products)))
            
            # Customers count
            customers = self.customer_model.get_all_customers()
            self.summary_cards['customers'].setText(str(len(customers)))
            
            # Pending orders
            try:
                pending_query = "SELECT COUNT(*) as count FROM online_orders WHERE delivery_status IN ('pending', 'confirmed', 'preparing')"
                pending = self.db.fetch_one(pending_query)
                self.summary_cards['pending'].setText(str(pending['count']) if pending else "0")
            except Exception as e:
                print(f"Error loading pending orders: {e}")
                self.summary_cards['pending'].setText("0")
            
            # Recent sales
            recent_sales = self.sale_model.get_daily_sales()
            self.recent_sales_table.setRowCount(len(recent_sales))
            for i, sale in enumerate(recent_sales):
                self.recent_sales_table.setItem(i, 0, QTableWidgetItem(sale['invoice_number']))
                self.recent_sales_table.setItem(i, 1, QTableWidgetItem(sale.get('customer_name', 'Walk-in') or "Walk-in"))
                self.recent_sales_table.setItem(i, 2, QTableWidgetItem(format_currency(sale['total_amount'])))
                
                if isinstance(sale['created_at'], datetime):
                    time_str = sale['created_at'].strftime('%H:%M:%S')
                else:
                    time_str = str(sale['created_at'])
                self.recent_sales_table.setItem(i, 3, QTableWidgetItem(time_str))
                
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def create_pos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        message = QLabel("🛒 Point of Sale")
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(message)
        
        info = QLabel("Use the 'Billing' tab for faster checkout")
        info.setAlignment(Qt.AlignCenter)
        info.setFont(QFont("Arial", 12))
        info.setStyleSheet("color: #666;")
        layout.addWidget(info)
        
        return tab
    
    def handle_alert_click(self, alert_data):
        if alert_data['type'] == 'view_product':
            self.tab_widget.setCurrentIndex(1)  # Products tab
            self.statusBar().showMessage(f"Viewing product ID: {alert_data['product_id']}", 3000)
    
    def on_billing_completed(self, bill_data):
        self.load_dashboard_data()
        self.statusBar().showMessage(f"✅ Bill #{bill_data['invoice']} completed - {format_currency(bill_data['total'])}", 5000)
    
    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            import sys
            import subprocess
            subprocess.Popen([sys.executable, 'main.py'])
            sys.exit()
    
    def show_about(self):
        QMessageBox.about(self, "About Supermarket ERP",
                         f"<h2>Supermarket ERP System</h2>"
                         f"<p>Version: 1.0.0</p>"
                         f"<p>A complete ERP solution for supermarkets</p>"
                         f"<p>Features:</p>"
                         f"<ul>"
                         f"<li>Products Management</li>"
                         f"<li>Customer Management</li>"
                         f"<li>Fast Billing with Barcode</li>"
                         f"<li>Online Ordering & Delivery</li>"
                         f"<li>Self Checkout Kiosks</li>"
                         f"<li>Goods Inward</li>"
                         f"<li>Stock Audit & Picking</li>"
                         f"<li>Purchase Orders</li>"
                         f"<li>Reports & Analytics</li>"
                         f"<li>Business Alerts</li>"
                         f"<li>User Management</li>"
                         f"</ul>"
                         f"<p>Developed with PyQt5 and MySQL</p>")
