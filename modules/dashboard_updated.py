# Add these imports at the top of dashboard.py
from modules.online_ordering.online_orders import OnlineOrderingModule
from modules.kiosk.self_checkout import SelfCheckoutKiosk
from modules.goods_inward.goods_inward import GoodsInwardModule
from modules.alerts.business_alerts import BusinessAlertsModule
from modules.audit.stock_audit import StockAuditModule, StockPickingModule
from modules.purchases.centralized_purchases import CentralizedPurchasesModule
from modules.billing.superfast_billing import SuperfastBillingModule

# Then in the init_ui method, add these tabs:

# Online Ordering tab
self.online_ordering_tab = OnlineOrderingModule(self.user)
self.tab_widget.addTab(self.online_ordering_tab, "🛵 Online Orders")

# Self Checkout tab
self.kiosk_tab = SelfCheckoutKiosk(self.user)
self.tab_widget.addTab(self.kiosk_tab, "🛒 Self Checkout")

# Goods Inward tab
self.goods_inward_tab = GoodsInwardModule(self.user)
self.tab_widget.addTab(self.goods_inward_tab, "📦 Goods Inward")

# Business Alerts tab
self.alerts_tab = BusinessAlertsModule(self.user)
self.alerts_tab.alert_clicked.connect(self.handle_alert_click)
self.tab_widget.addTab(self.alerts_tab, "🔔 Alerts")

# Stock Audit tab
self.audit_tab = StockAuditModule(self.user)
self.tab_widget.addTab(self.audit_tab, "📊 Stock Audit")

# Stock Picking tab
self.picking_tab = StockPickingModule(self.user)
self.tab_widget.addTab(self.picking_tab, "📦 Stock Picking")

# Centralized Purchases tab
self.purchases_tab = CentralizedPurchasesModule(self.user)
self.tab_widget.addTab(self.purchases_tab, "📋 Purchases")

# Superfast Billing tab
self.billing_tab = SuperfastBillingModule(self.user)
self.billing_tab.billing_completed.connect(self.on_billing_completed)
self.tab_widget.addTab(self.billing_tab, "⚡ Fast Billing")

# Add this method to handle alert clicks
def handle_alert_click(self, alert_data):
    if alert_data['type'] == 'view_product':
        # Switch to products tab and load product
        self.tab_widget.setCurrentIndex(2)  # Products tab index
        # You would then load the specific product

def on_billing_completed(self, bill_data):
    # Refresh dashboard data after billing
    self.load_dashboard_data()
    # Show notification
    self.statusBar().showMessage(f"Bill #{bill_data['invoice']} completed - ₹{bill_data['total']:,.2f}", 3000)
