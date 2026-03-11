import os
import sqlite3
import hashlib
from datetime import datetime

def init_database():
    """Initialize SQLite database with all tables"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'supermarket.db')
    
    # Remove existing database if it exists (for clean start)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ===========================================
    # Create tables
    # ===========================================
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'cashier',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT,
            supplier_id INTEGER,
            cost_price REAL,
            selling_price REAL,
            quantity INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 10,
            expiry_date DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Customers table
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE,
            email TEXT,
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            customer_id INTEGER,
            total_amount REAL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'cash',
            billing_type TEXT DEFAULT 'regular',
            cash_given REAL,
            cash_return REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Sale items table
    cursor.execute('''
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Suppliers table
    cursor.execute('''
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_code TEXT UNIQUE,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            gst_number TEXT,
            payment_terms TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Purchase orders table
    cursor.execute('''
        CREATE TABLE purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            supplier_id INTEGER,
            order_date DATE,
            expected_delivery DATE,
            status TEXT DEFAULT 'draft',
            total_items INTEGER,
            total_amount REAL,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            grand_total REAL,
            created_by INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Purchase order items
    cursor.execute('''
        CREATE TABLE purchase_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_cost REAL,
            total_cost REAL,
            received_quantity INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Online orders table
    cursor.execute('''
        CREATE TABLE online_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            delivery_address TEXT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_date DATETIME,
            delivery_status TEXT DEFAULT 'pending',
            payment_method TEXT DEFAULT 'cash',
            payment_status TEXT DEFAULT 'pending',
            total_amount REAL,
            delivery_charge REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            order_notes TEXT,
            assigned_delivery_person TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Online order items
    cursor.execute('''
        CREATE TABLE online_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            FOREIGN KEY (order_id) REFERENCES online_orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Kiosk sessions
    cursor.execute('''
        CREATE TABLE kiosk_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            kiosk_number TEXT,
            customer_id INTEGER,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'active',
            total_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Kiosk cart items
    cursor.execute('''
        CREATE TABLE kiosk_cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES kiosk_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Goods inward
    cursor.execute('''
        CREATE TABLE goods_inward (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT,
            invoice_number TEXT UNIQUE NOT NULL,
            supplier_name TEXT,
            supplier_invoice TEXT,
            received_date DATE,
            received_by INTEGER,
            total_items INTEGER,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (received_by) REFERENCES users(id)
        )
    ''')
    
    # Goods inward items
    cursor.execute('''
        CREATE TABLE goods_inward_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goods_inward_id INTEGER,
            product_id INTEGER,
            quantity_received INTEGER,
            quantity_ordered INTEGER,
            unit_cost REAL,
            total_cost REAL,
            expiry_date DATE,
            batch_number TEXT,
            quality_check TEXT DEFAULT 'pending',
            notes TEXT,
            FOREIGN KEY (goods_inward_id) REFERENCES goods_inward(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'info',
            title TEXT NOT NULL,
            message TEXT,
            product_id INTEGER,
            is_read INTEGER DEFAULT 0,
            is_resolved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Stock audits
    cursor.execute('''
        CREATE TABLE stock_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_number TEXT UNIQUE NOT NULL,
            audit_date DATE,
            conducted_by INTEGER,
            status TEXT DEFAULT 'draft',
            total_items_audited INTEGER DEFAULT 0,
            total_discrepancies INTEGER DEFAULT 0,
            total_value_discrepancy REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (conducted_by) REFERENCES users(id)
        )
    ''')
    
    # Stock audit items
    cursor.execute('''
        CREATE TABLE stock_audit_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id INTEGER,
            product_id INTEGER,
            system_quantity INTEGER,
            physical_quantity INTEGER,
            discrepancy INTEGER,
            unit_cost REAL,
            discrepancy_value REAL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            FOREIGN KEY (audit_id) REFERENCES stock_audits(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Stock pickings
    cursor.execute('''
        CREATE TABLE stock_pickings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            picking_number TEXT UNIQUE NOT NULL,
            picking_type TEXT NOT NULL,
            reference_type TEXT NOT NULL,
            reference_id INTEGER NOT NULL,
            assigned_to INTEGER,
            status TEXT DEFAULT 'pending',
            total_items INTEGER DEFAULT 0,
            picked_items INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    ''')
    
    # Stock picking items
    cursor.execute('''
        CREATE TABLE stock_picking_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            picking_id INTEGER,
            product_id INTEGER,
            quantity_required INTEGER,
            quantity_picked INTEGER DEFAULT 0,
            location_from TEXT,
            location_to TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            FOREIGN KEY (picking_id) REFERENCES stock_pickings(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # ===========================================
    # Insert default data
    # ===========================================
    
    # Insert admin user (password: admin123)
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password, 'Administrator', 'admin'))
    
    # Insert default walk-in customer
    cursor.execute('''
        INSERT INTO customers (name, phone, email, address, loyalty_points)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Walk-in Customer', '0000000000', '', 'Default Customer', 0))
    
    # Insert sample products
    sample_products = [
        ('8901234567890', 'Basmati Rice 5kg', 'Groceries', 250.00, 320.00, 50, 10),
        ('8901234567891', 'Toor Dal 1kg', 'Groceries', 80.00, 110.00, 30, 5),
        ('8901234567892', 'Sunflower Oil 1L', 'Cooking Oil', 90.00, 130.00, 40, 8),
        ('8901234567893', 'Wheat Flour 5kg', 'Groceries', 150.00, 200.00, 25, 5),
        ('8901234567894', 'Sugar 1kg', 'Groceries', 35.00, 48.00, 100, 20)
    ]
    
    for product in sample_products:
        cursor.execute('''
            INSERT INTO products (barcode, name, category, cost_price, selling_price, quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', product)
    
    # Insert sample suppliers
    suppliers = [
        ('SUP001', 'Global Foods Ltd', 'John Smith', '9876543210', 'john@globalfoods.com', 'Mumbai'),
        ('SUP002', 'Fresh Produce Co', 'Jane Doe', '9876543211', 'jane@freshproduce.com', 'Delhi')
    ]
    
    for supplier in suppliers:
        cursor.execute('''
            INSERT INTO suppliers (supplier_code, name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', supplier)
    
    # Commit all changes
    conn.commit()
    
    # Get table count
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_count = len(tables)
    
    conn.close()
    
    print("✅ SQLite database initialized successfully!")
    print(f"📁 Database location: {db_path}")
    print("🔑 Default login: admin / admin123")
    print(f"📊 Tables created: {table_count} tables")

if __name__ == "__main__":
    init_database()
