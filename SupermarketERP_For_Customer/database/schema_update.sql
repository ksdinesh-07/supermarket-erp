-- Add new tables for additional features

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
);

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
);

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
);

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
);

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
);

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
);

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
);

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
);

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
);

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
);

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
);

-- Centralized Purchases
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(200),
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
);

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
);

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
);

-- Fast Billing (enhance existing sales table)
ALTER TABLE sales ADD COLUMN IF NOT EXISTS billing_type ENUM('regular', 'quick', 'self_checkout') DEFAULT 'regular';
ALTER TABLE sales ADD COLUMN IF NOT EXISTS payment_method ENUM('cash', 'card', 'upi', 'mixed') DEFAULT 'cash';
ALTER TABLE sales ADD COLUMN IF NOT EXISTS card_number VARCHAR(50);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS upi_id VARCHAR(100);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS cash_given DECIMAL(10,2);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS cash_return DECIMAL(10,2);

-- Create trigger for low stock alerts
DELIMITER //
CREATE TRIGGER IF NOT EXISTS after_product_update
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
DELIMITER ;

-- Create trigger for expiry alerts
DELIMITER //
CREATE TRIGGER IF NOT EXISTS after_product_insert
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

-- Insert sample supplier
INSERT INTO suppliers (supplier_code, name, contact_person, phone, email, address) VALUES
('SUP001', 'Global Foods Ltd', 'John Smith', '9876543210', 'john@globalfoods.com', 'Mumbai')
ON DUPLICATE KEY UPDATE name = VALUES(name);
