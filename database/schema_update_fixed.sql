-- Use the existing database
USE supermarket_erp;

-- Online Orders table
CREATE TABLE IF NOT EXISTS online_orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    customer_address TEXT,
    delivery_address TEXT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATETIME,
    delivery_status ENUM('pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'pending',
    payment_method ENUM('cash', 'card', 'online') DEFAULT 'cash',
    payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    delivery_charge DECIMAL(10,2) DEFAULT 0,
    discount DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    order_notes TEXT,
    assigned_delivery_person VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    INDEX idx_order_number (order_number),
    INDEX idx_delivery_status (delivery_status),
    INDEX idx_delivery_date (delivery_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Online Order Items
CREATE TABLE IF NOT EXISTS online_order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES online_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Self Checkout Kiosk Sessions
CREATE TABLE IF NOT EXISTS kiosk_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    kiosk_number VARCHAR(20),
    customer_id INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    total_amount DECIMAL(10,2) DEFAULT 0,
    payment_status ENUM('pending', 'completed') DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    INDEX idx_session_id (session_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Kiosk Cart Items
CREATE TABLE IF NOT EXISTS kiosk_cart_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES kiosk_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Goods Inward (Purchase Receiving)
CREATE TABLE IF NOT EXISTS goods_inward (
    id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(200),
    supplier_invoice VARCHAR(100),
    received_date DATE,
    received_by INT,
    total_items INT,
    total_amount DECIMAL(10,2),
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (received_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_invoice_number (invoice_number),
    INDEX idx_received_date (received_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Goods Inward Items
CREATE TABLE IF NOT EXISTS goods_inward_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    goods_inward_id INT,
    product_id INT,
    quantity_received INT,
    quantity_ordered INT,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    expiry_date DATE,
    batch_number VARCHAR(50),
    quality_check ENUM('passed', 'failed', 'pending') DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (goods_inward_id) REFERENCES goods_inward(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Business Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type ENUM('low_stock', 'expiry', 'sales_target', 'price_change', 'system') NOT NULL,
    severity ENUM('info', 'warning', 'critical') DEFAULT 'info',
    title VARCHAR(200) NOT NULL,
    message TEXT,
    product_id INT,
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    INDEX idx_alert_type (alert_type),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Stock Audit
CREATE TABLE IF NOT EXISTS stock_audits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    audit_number VARCHAR(50) UNIQUE NOT NULL,
    audit_date DATE,
    conducted_by INT,
    status ENUM('draft', 'in_progress', 'completed', 'cancelled') DEFAULT 'draft',
    total_items_audited INT DEFAULT 0,
    total_discrepancies INT DEFAULT 0,
    total_value_discrepancy DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (conducted_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_number (audit_number),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Stock Audit Items
CREATE TABLE IF NOT EXISTS stock_audit_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    audit_id INT,
    product_id INT,
    system_quantity INT,
    physical_quantity INT,
    discrepancy INT,
    unit_cost DECIMAL(10,2),
    discrepancy_value DECIMAL(10,2),
    status ENUM('pending', 'verified', 'adjusted') DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (audit_id) REFERENCES stock_audits(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Stock Pickings (for orders)
CREATE TABLE IF NOT EXISTS stock_pickings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    picking_number VARCHAR(50) UNIQUE NOT NULL,
    picking_type ENUM('sale', 'transfer', 'return') NOT NULL,
    reference_type ENUM('sale', 'online_order', 'transfer') NOT NULL,
    reference_id INT NOT NULL,
    assigned_to INT,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    total_items INT DEFAULT 0,
    picked_items INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_picking_number (picking_number),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Stock Picking Items
CREATE TABLE IF NOT EXISTS stock_picking_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    picking_id INT,
    product_id INT,
    quantity_required INT,
    quantity_picked INT DEFAULT 0,
    location_from VARCHAR(100),
    location_to VARCHAR(100),
    status ENUM('pending', 'picked', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (picking_id) REFERENCES stock_pickings(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_code VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    gst_number VARCHAR(50),
    payment_terms VARCHAR(100),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_supplier_code (supplier_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Centralized Purchases - Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INT,
    order_date DATE,
    expected_delivery DATE,
    status ENUM('draft', 'sent', 'confirmed', 'partial', 'received', 'cancelled') DEFAULT 'draft',
    total_items INT,
    total_amount DECIMAL(10,2),
    discount DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    grand_total DECIMAL(10,2),
    created_by INT,
    approved_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_po_number (po_number),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Purchase Order Items
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    product_id INT,
    quantity INT,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    received_quantity INT DEFAULT 0,
    status ENUM('pending', 'partial', 'received') DEFAULT 'pending',
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Now add columns to sales table (checking existence with a different approach)
-- First check if billing_type column exists, if not add it
SET @dbname = DATABASE();
SET @tablename = "sales";
SET @columnname = "billing_type";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " ENUM('regular', 'quick', 'self_checkout') DEFAULT 'regular';")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- payment_method column
SET @columnname = "payment_method";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " ENUM('cash', 'card', 'upi', 'mixed') DEFAULT 'cash';")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- card_number column
SET @columnname = "card_number";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " VARCHAR(50);")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- upi_id column
SET @columnname = "upi_id";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " VARCHAR(100);")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- cash_given column
SET @columnname = "cash_given";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " DECIMAL(10,2);")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- cash_return column
SET @columnname = "cash_return";
SET @preparedStatement = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    "SELECT 1",
    CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " DECIMAL(10,2);")
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Create triggers for alerts
DELIMITER //

DROP TRIGGER IF EXISTS after_product_update//
CREATE TRIGGER after_product_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.quantity <= NEW.reorder_level AND OLD.quantity > OLD.reorder_level THEN
        INSERT INTO alerts (alert_type, severity, title, message, product_id)
        VALUES ('low_stock', 'warning', CONCAT('Low Stock Alert: ', NEW.name), 
                CONCAT('Current stock: ', NEW.quantity, ' (Reorder level: ', NEW.reorder_level, ')'), 
                NEW.id);
    END IF;
END//

DROP TRIGGER IF EXISTS after_product_insert//
CREATE TRIGGER after_product_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    IF NEW.expiry_date IS NOT NULL AND NEW.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN
        INSERT INTO alerts (alert_type, severity, title, message, product_id)
        VALUES ('expiry', 'warning', CONCAT('Expiry Alert: ', NEW.name), 
                CONCAT('Expires on: ', NEW.expiry_date), 
                NEW.id);
    END IF;
END//

DELIMITER ;

-- Insert sample supplier if not exists
INSERT INTO suppliers (supplier_code, name, contact_person, phone, email, address) 
SELECT 'SUP001', 'Global Foods Ltd', 'John Smith', '9876543210', 'john@globalfoods.com', 'Mumbai'
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_code = 'SUP001');

-- Insert another sample supplier if not exists
INSERT INTO suppliers (supplier_code, name, contact_person, phone, email, address) 
SELECT 'SUP002', 'Fresh Produce Co', 'Jane Doe', '9876543211', 'jane@freshproduce.com', 'Delhi'
WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_code = 'SUP002');

-- Insert sample online orders if not exists
INSERT INTO online_orders (order_number, customer_name, customer_phone, customer_address, delivery_address, total_amount, delivery_status)
SELECT 'ORD-20240315-001', 'Rahul Sharma', '9876543212', '123 MG Road, Bangalore', '123 MG Road, Bangalore', 1250.00, 'pending'
WHERE NOT EXISTS (SELECT 1 FROM online_orders WHERE order_number = 'ORD-20240315-001');

INSERT INTO online_orders (order_number, customer_name, customer_phone, customer_address, delivery_address, total_amount, delivery_status)
SELECT 'ORD-20240315-002', 'Priya Patel', '9876543213', '456 Park Street, Mumbai', '456 Park Street, Mumbai', 890.00, 'confirmed'
WHERE NOT EXISTS (SELECT 1 FROM online_orders WHERE order_number = 'ORD-20240315-002');

INSERT INTO online_orders (order_number, customer_name, customer_phone, customer_address, delivery_address, total_amount, delivery_status, assigned_delivery_person)
SELECT 'ORD-20240315-003', 'Amit Kumar', '9876543214', '789 Lake Road, Chennai', '789 Lake Road, Chennai', 2340.00, 'out_for_delivery', 'Raju Delivery'
WHERE NOT EXISTS (SELECT 1 FROM online_orders WHERE order_number = 'ORD-20240315-003');

-- Insert sample purchase orders if not exists
INSERT INTO purchase_orders (po_number, supplier_id, order_date, expected_delivery, status, total_items, total_amount, grand_total, created_by)
SELECT 'PO-20240315-001', 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'sent', 5, 15000.00, 17700.00, 1
WHERE NOT EXISTS (SELECT 1 FROM purchase_orders WHERE po_number = 'PO-20240315-001');

INSERT INTO purchase_orders (po_number, supplier_id, order_date, expected_delivery, status, total_items, total_amount, grand_total, created_by)
SELECT 'PO-20240315-002', 2, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'draft', 3, 8500.00, 10030.00, 1
WHERE NOT EXISTS (SELECT 1 FROM purchase_orders WHERE po_number = 'PO-20240315-002');

-- Insert sample kiosk sessions if not exists
INSERT INTO kiosk_sessions (session_id, kiosk_number, status, total_amount, payment_status)
SELECT 'SESS-001', 'KIO-001', 'completed', 560.00, 'completed'
WHERE NOT EXISTS (SELECT 1 FROM kiosk_sessions WHERE session_id = 'SESS-001');

INSERT INTO kiosk_sessions (session_id, kiosk_number, status, total_amount)
SELECT 'SESS-002', 'KIO-002', 'active', 320.00
WHERE NOT EXISTS (SELECT 1 FROM kiosk_sessions WHERE session_id = 'SESS-002');

-- Insert sample goods inward if not exists
INSERT INTO goods_inward (invoice_number, po_number, supplier_name, received_date, received_by, total_items, total_amount, status)
SELECT 'INV-20240315-001', 'PO-20240315-001', 'Global Foods Ltd', CURDATE(), 1, 5, 15000.00, 'completed'
WHERE NOT EXISTS (SELECT 1 FROM goods_inward WHERE invoice_number = 'INV-20240315-001');

-- Create some alerts if not exists
INSERT INTO alerts (alert_type, severity, title, message, product_id)
SELECT 'low_stock', 'warning', 'Low Stock Alert: Basmati Rice 5kg', 'Current stock: 5 (Reorder level: 10)', 1
WHERE NOT EXISTS (SELECT 1 FROM alerts WHERE title = 'Low Stock Alert: Basmati Rice 5kg' AND is_resolved = FALSE);

INSERT INTO alerts (alert_type, severity, title, message, product_id)
SELECT 'expiry', 'warning', 'Expiry Alert: Sunflower Oil 1L', 'Expires in 15 days', 3
WHERE NOT EXISTS (SELECT 1 FROM alerts WHERE title = 'Expiry Alert: Sunflower Oil 1L' AND is_resolved = FALSE);
