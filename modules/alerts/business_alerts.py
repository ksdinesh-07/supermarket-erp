from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QGroupBox, QGridLayout, QComboBox,
                           QDateTimeEdit, QMessageBox, QFrame, QSplitter,
                           QTextEdit, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from datetime import datetime, timedelta

class BusinessAlertsModule(QWidget):
    alert_clicked = pyqtSignal(dict)
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        self.load_alerts()
        
        # Auto-refresh every 60 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_alerts)
        self.timer.start(60000)
        
        # Check for new alerts
        self.check_for_alerts()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with statistics
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Alert list
        left_panel = self.create_alert_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Alert details
        right_panel = self.create_alert_details_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Alerts")
        self.refresh_btn.clicked.connect(self.load_alerts)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.mark_read_btn = QPushButton("✓ Mark Selected as Read")
        self.mark_read_btn.clicked.connect(self.mark_selected_read)
        buttons_layout.addWidget(self.mark_read_btn)
        
        self.mark_all_read_btn = QPushButton("✓✓ Mark All as Read")
        self.mark_all_read_btn.clicked.connect(self.mark_all_read)
        buttons_layout.addWidget(self.mark_all_read_btn)
        
        self.resolve_btn = QPushButton("✅ Resolve Selected")
        self.resolve_btn.clicked.connect(self.resolve_selected)
        buttons_layout.addWidget(self.resolve_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def create_header(self):
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 10px;
                color: white;
            }
        """)
        header.setFixedHeight(100)
        
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("🔔 Business Alerts & Notifications")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Alert statistics
        stats_layout = QHBoxLayout()
        
        self.critical_count = QLabel("🔴 Critical: 0")
        self.critical_count.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(self.critical_count)
        
        self.warning_count = QLabel("🟡 Warnings: 0")
        self.warning_count.setFont(QFont("Arial", 12))
        stats_layout.addWidget(self.warning_count)
        
        self.info_count = QLabel("🔵 Info: 0")
        self.info_count.setFont(QFont("Arial", 12))
        stats_layout.addWidget(self.info_count)
        
        layout.addLayout(stats_layout)
        
        return header
    
    def create_alert_list_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QGridLayout()
        
        # Type filter
        filter_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_filter = QComboBox()
        self.type_filter.addItems(['All', 'low_stock', 'expiry', 'sales_target', 'price_change', 'system'])
        self.type_filter.currentTextChanged.connect(self.load_alerts)
        filter_layout.addWidget(self.type_filter, 0, 1)
        
        # Severity filter
        filter_layout.addWidget(QLabel("Severity:"), 0, 2)
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(['All', 'critical', 'warning', 'info'])
        self.severity_filter.currentTextChanged.connect(self.load_alerts)
        filter_layout.addWidget(self.severity_filter, 0, 3)
        
        # Read/Unread filter
        filter_layout.addWidget(QLabel("Status:"), 1, 0)
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'Unread', 'Read', 'Resolved'])
        self.status_filter.currentTextChanged.connect(self.load_alerts)
        filter_layout.addWidget(self.status_filter, 1, 1)
        
        # Date range
        filter_layout.addWidget(QLabel("From:"), 1, 2)
        self.date_from = QDateTimeEdit()
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.date_from.setCalendarPopup(True)
        self.date_from.dateTimeChanged.connect(self.load_alerts)
        filter_layout.addWidget(self.date_from, 1, 3)
        
        filter_layout.addWidget(QLabel("To:"), 2, 2)
        self.date_to = QDateTimeEdit()
        self.date_to.setDateTime(QDateTime.currentDateTime())
        self.date_to.setCalendarPopup(True)
        self.date_to.dateTimeChanged.connect(self.load_alerts)
        filter_layout.addWidget(self.date_to, 2, 3)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(7)
        self.alerts_table.setHorizontalHeaderLabels([
            "", "Type", "Severity", "Title", "Message", "Time", "Status"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_table.itemClicked.connect(self.on_alert_selected)
        layout.addWidget(self.alerts_table)
        
        return panel
    
    def create_alert_details_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Alert details
        details_group = QGroupBox("Alert Details")
        details_layout = QGridLayout()
        
        self.alert_type_label = QLabel("-")
        details_layout.addWidget(QLabel("Type:"), 0, 0)
        details_layout.addWidget(self.alert_type_label, 0, 1)
        
        self.alert_severity_label = QLabel("-")
        details_layout.addWidget(QLabel("Severity:"), 1, 0)
        details_layout.addWidget(self.alert_severity_label, 1, 1)
        
        self.alert_time_label = QLabel("-")
        details_layout.addWidget(QLabel("Time:"), 2, 0)
        details_layout.addWidget(self.alert_time_label, 2, 1)
        
        self.alert_status_label = QLabel("-")
        details_layout.addWidget(QLabel("Status:"), 3, 0)
        details_layout.addWidget(self.alert_status_label, 3, 1)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Alert message
        message_group = QGroupBox("Message")
        message_layout = QVBoxLayout()
        self.alert_message = QTextEdit()
        self.alert_message.setReadOnly(True)
        message_layout.addWidget(self.alert_message)
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        
        self.view_product_btn = QPushButton("🔍 View Product")
        self.view_product_btn.clicked.connect(self.view_related_product)
        self.view_product_btn.setEnabled(False)
        actions_layout.addWidget(self.view_product_btn)
        
        self.mark_read_detail_btn = QPushButton("✓ Mark as Read")
        self.mark_read_detail_btn.clicked.connect(self.mark_current_read)
        actions_layout.addWidget(self.mark_read_detail_btn)
        
        self.resolve_detail_btn = QPushButton("✅ Resolve")
        self.resolve_detail_btn.clicked.connect(self.resolve_current)
        actions_layout.addWidget(self.resolve_detail_btn)
        
        actions_layout.addStretch()
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        return panel
    
    def check_for_alerts(self):
        """Check for various business conditions and create alerts"""
        try:
            # Check low stock
            self.check_low_stock()
            
            # Check expiring products
            self.check_expiring_products()
            
            # Check sales targets
            self.check_sales_targets()
            
            # Check price changes
            self.check_price_changes()
            
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    def check_low_stock(self):
        """Check for low stock products and create alerts"""
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM alerts 
                    WHERE product_id = p.id 
                    AND alert_type = 'low_stock' 
                    AND is_resolved = FALSE 
                    AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)) as recent_alert
            FROM products p
            WHERE p.quantity <= p.reorder_level
            AND p.quantity > 0
        """
        low_stock = self.db.fetch_all(query)
        
        for product in low_stock:
            if product['recent_alert'] == 0:  # No recent alert
                severity = 'critical' if product['quantity'] == 0 else 'warning'
                title = f"Low Stock: {product['name']}"
                message = f"Current stock: {product['quantity']} (Reorder level: {product['reorder_level']})"
                
                self.create_alert('low_stock', severity, title, message, product['id'])
    
    def check_expiring_products(self):
        """Check for products nearing expiry"""
        query = """
            SELECT * FROM products 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            AND expiry_date >= CURDATE()
        """
        expiring = self.db.fetch_all(query)
        
        for product in expiring:
            days_left = (product['expiry_date'] - datetime.now().date()).days
            
            # Check if alert already exists for this product
            check_query = """
                SELECT id FROM alerts 
                WHERE product_id = %s 
                AND alert_type = 'expiry' 
                AND is_resolved = FALSE
            """
            existing = self.db.fetch_one(check_query, (product['id'],))
            
            if not existing:
                if days_left <= 7:
                    severity = 'critical'
                elif days_left <= 15:
                    severity = 'warning'
                else:
                    severity = 'info'
                
                title = f"Expiry Alert: {product['name']}"
                message = f"Product expires in {days_left} days on {product['expiry_date']}"
                
                self.create_alert('expiry', severity, title, message, product['id'])
    
    def check_sales_targets(self):
        """Check daily sales targets"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's sales
        query = """
            SELECT COALESCE(SUM(total_amount), 0) as daily_sales
            FROM sales
            WHERE DATE(created_at) = %s
        """
        result = self.db.fetch_one(query, (today,))
        daily_sales = result['daily_sales'] if result else 0
        
        # Get target (you can set this in config)
        target = 50000  # Example: ₹50,000 daily target
        
        if daily_sales < target * 0.5:
            # Less than 50% of target
            title = "⚠️ Low Sales Alert"
            message = f"Today's sales: {format_currency(daily_sales)} (Target: {format_currency(target)})"
            self.create_alert('sales_target', 'warning', title, message)
        
        elif daily_sales >= target:
            # Target achieved
            title = "🎯 Sales Target Achieved!"
            message = f"Congratulations! Today's sales: {format_currency(daily_sales)}"
            self.create_alert('sales_target', 'info', title, message)
    
    def check_price_changes(self):
        """Check for significant price changes"""
        query = """
            SELECT id, name, selling_price, cost_price,
                   (selling_price - cost_price) / cost_price * 100 as margin
            FROM products
            WHERE cost_price > 0
        """
        products = self.db.fetch_all(query)
        
        for product in products:
            margin = product['margin']
            
            if margin < 10:  # Less than 10% margin
                title = f"Low Margin Alert: {product['name']}"
                message = f"Current margin: {margin:.1f}% (Selling: {format_currency(product['selling_price'])}, Cost: {format_currency(product['cost_price'])})"
                self.create_alert('price_change', 'warning', title, message, product['id'])
    
    def create_alert(self, alert_type, severity, title, message, product_id=None):
        """Create a new alert in the database"""
        try:
            # Check if similar alert already exists
            check_query = """
                SELECT id FROM alerts 
                WHERE alert_type = %s 
                AND title = %s 
                AND is_resolved = FALSE
                AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """
            existing = self.db.fetch_one(check_query, (alert_type, title))
            
            if not existing:
                query = """
                    INSERT INTO alerts (alert_type, severity, title, message, product_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.db.execute_query(query, (alert_type, severity, title, message, product_id))
                
        except Exception as e:
            print(f"Error creating alert: {e}")
    
    def load_alerts(self):
        """Load alerts based on filters"""
        try:
            alert_type = self.type_filter.currentText()
            severity = self.severity_filter.currentText()
            status = self.status_filter.currentText()
            date_from = self.date_from.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            date_to = self.date_to.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            
            query = """
                SELECT a.*, 
                       CASE 
                           WHEN a.is_resolved THEN 'Resolved'
                           WHEN a.is_read THEN 'Read'
                           ELSE 'Unread'
                       END as display_status
                FROM alerts a
                WHERE a.created_at BETWEEN %s AND %s
            """
            params = [date_from, date_to]
            
            if alert_type != 'All':
                query += " AND a.alert_type = %s"
                params.append(alert_type)
            
            if severity != 'All':
                query += " AND a.severity = %s"
                params.append(severity)
            
            if status == 'Unread':
                query += " AND a.is_read = FALSE AND a.is_resolved = FALSE"
            elif status == 'Read':
                query += " AND a.is_read = TRUE AND a.is_resolved = FALSE"
            elif status == 'Resolved':
                query += " AND a.is_resolved = TRUE"
            
            query += " ORDER BY a.created_at DESC"
            
            alerts = self.db.fetch_all(query, params)
            
            # Update statistics
            critical = sum(1 for a in alerts if a['severity'] == 'critical' and not a['is_resolved'])
            warning = sum(1 for a in alerts if a['severity'] == 'warning' and not a['is_resolved'])
            info = sum(1 for a in alerts if a['severity'] == 'info' and not a['is_resolved'])
            
            self.critical_count.setText(f"🔴 Critical: {critical}")
            self.warning_count.setText(f"🟡 Warnings: {warning}")
            self.info_count.setText(f"🔵 Info: {info}")
            
            # Update table
            self.alerts_table.setRowCount(len(alerts))
            for i, alert in enumerate(alerts):
                # Checkbox
                chk = QTableWidgetItem()
                chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                chk.setCheckState(Qt.Unchecked)
                self.alerts_table.setItem(i, 0, chk)
                
                # Type with icon
                type_icon = self.get_alert_icon(alert['alert_type'])
                type_item = QTableWidgetItem(f"{type_icon} {alert['alert_type'].replace('_', ' ').title()}")
                self.alerts_table.setItem(i, 1, type_item)
                
                # Severity with color
                severity_item = QTableWidgetItem(alert['severity'].upper())
                if alert['severity'] == 'critical':
                    severity_item.setForeground(QColor('#F44336'))
                    severity_item.setBackground(QColor('#FFEBEE'))
                elif alert['severity'] == 'warning':
                    severity_item.setForeground(QColor('#FF9800'))
                    severity_item.setBackground(QColor('#FFF3E0'))
                else:
                    severity_item.setForeground(QColor('#2196F3'))
                    severity_item.setBackground(QColor('#E3F2FD'))
                self.alerts_table.setItem(i, 2, severity_item)
                
                # Title (bold if unread)
                title_item = QTableWidgetItem(alert['title'])
                if not alert['is_read'] and not alert['is_resolved']:
                    font = QFont()
                    font.setBold(True)
                    title_item.setFont(font)
                self.alerts_table.setItem(i, 3, title_item)
                
                # Message (truncated)
                message = alert['message'][:50] + "..." if len(alert['message']) > 50 else alert['message']
                self.alerts_table.setItem(i, 4, QTableWidgetItem(message))
                
                # Time
                time_str = alert['created_at'].strftime('%H:%M %d/%m') if alert['created_at'] else '-'
                self.alerts_table.setItem(i, 5, QTableWidgetItem(time_str))
                
                # Status
                status_item = QTableWidgetItem(alert['display_status'])
                if alert['display_status'] == 'Resolved':
                    status_item.setForeground(QColor('#4CAF50'))
                elif alert['display_status'] == 'Read':
                    status_item.setForeground(QColor('#9E9E9E'))
                self.alerts_table.setItem(i, 6, status_item)
            
        except Exception as e:
            print(f"Error loading alerts: {e}")
    
    def get_alert_icon(self, alert_type):
        icons = {
            'low_stock': '📦',
            'expiry': '⏰',
            'sales_target': '🎯',
            'price_change': '💰',
            'system': '⚙️'
        }
        return icons.get(alert_type, '🔔')
    
    def on_alert_selected(self, item):
        row = item.row()
        self.current_alert_row = row
        
        # Get alert details
        title = self.alerts_table.item(row, 3).text()
        query = "SELECT * FROM alerts WHERE title = %s ORDER BY created_at DESC LIMIT 1"
        alert = self.db.fetch_one(query, (title,))
        
        if alert:
            self.display_alert_details(alert)
            
            # Mark as read
            if not alert['is_read']:
                self.mark_alert_read(alert['id'])
                # Refresh to update bold
                self.load_alerts()
    
    def display_alert_details(self, alert):
        self.alert_type_label.setText(alert['alert_type'].replace('_', ' ').title())
        self.alert_severity_label.setText(alert['severity'].upper())
        
        if alert['severity'] == 'critical':
            self.alert_severity_label.setStyleSheet("color: #F44336; font-weight: bold;")
        elif alert['severity'] == 'warning':
            self.alert_severity_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            self.alert_severity_label.setStyleSheet("color: #2196F3;")
        
        time_str = alert['created_at'].strftime('%d/%m/%Y %H:%M:%S') if alert['created_at'] else '-'
        self.alert_time_label.setText(time_str)
        
        status = "Resolved" if alert['is_resolved'] else ("Read" if alert['is_read'] else "Unread")
        self.alert_status_label.setText(status)
        
        self.alert_message.setText(alert['message'])
        
        # Enable/disable buttons
        self.view_product_btn.setEnabled(alert['product_id'] is not None)
        self.current_alert = alert
    
    def mark_alert_read(self, alert_id):
        query = "UPDATE alerts SET is_read = TRUE WHERE id = %s"
        self.db.execute_query(query, (alert_id,))
    
    def mark_selected_read(self):
        for row in range(self.alerts_table.rowCount()):
            chk = self.alerts_table.item(row, 0)
            if chk and chk.checkState() == Qt.Checked:
                title = self.alerts_table.item(row, 3).text()
                query = "UPDATE alerts SET is_read = TRUE WHERE title = %s"
                self.db.execute_query(query, (title,))
        
        self.load_alerts()
        QMessageBox.information(self, "Success", "Selected alerts marked as read.")
    
    def mark_all_read(self):
        reply = QMessageBox.question(self, "Mark All Read", 
                                    "Mark all alerts as read?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = "UPDATE alerts SET is_read = TRUE WHERE is_resolved = FALSE"
            self.db.execute_query(query)
            self.load_alerts()
            QMessageBox.information(self, "Success", "All alerts marked as read.")
    
    def mark_current_read(self):
        if hasattr(self, 'current_alert'):
            self.mark_alert_read(self.current_alert['id'])
            self.load_alerts()
            self.display_alert_details(self.current_alert)
    
    def resolve_selected(self):
        for row in range(self.alerts_table.rowCount()):
            chk = self.alerts_table.item(row, 0)
            if chk and chk.checkState() == Qt.Checked:
                title = self.alerts_table.item(row, 3).text()
                query = "UPDATE alerts SET is_resolved = TRUE, resolved_at = NOW() WHERE title = %s"
                self.db.execute_query(query, (title,))
        
        self.load_alerts()
        QMessageBox.information(self, "Success", "Selected alerts resolved.")
    
    def resolve_current(self):
        if hasattr(self, 'current_alert'):
            reply = QMessageBox.question(self, "Resolve Alert", 
                                        "Mark this alert as resolved?",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                query = "UPDATE alerts SET is_resolved = TRUE, resolved_at = NOW() WHERE id = %s"
                self.db.execute_query(query, (self.current_alert['id'],))
                self.load_alerts()
                
                # Refresh display
                self.current_alert['is_resolved'] = True
                self.display_alert_details(self.current_alert)
    
    def view_related_product(self):
        if hasattr(self, 'current_alert') and self.current_alert['product_id']:
            # Emit signal to switch to product view
            self.alert_clicked.emit({
                'type': 'view_product',
                'product_id': self.current_alert['product_id']
            })

