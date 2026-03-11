import hashlib
from datetime import datetime
from database.connection import DatabaseConnection

class UserModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def authenticate(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
        user = self.db.fetch_one(query, (username, password_hash))
        
        if user:
            # Update last login
            update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
            self.db.execute_query(update_query, (user['id'],))
        
        return user
    
    def create_user(self, username, password, full_name, role):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = """
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (username, password_hash, full_name, role))
    
    def get_all_users(self):
        query = "SELECT id, username, full_name, role, created_at, last_login FROM users"
        return self.db.fetch_all(query)
    
    def update_user(self, user_id, full_name, role):
        query = "UPDATE users SET full_name = ?, role = ? WHERE id = ?"
        return self.db.execute_query(query, (full_name, role, user_id))
    
    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = ?"
        return self.db.execute_query(query, (user_id,))

class ProductModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_product(self, barcode, name, category, cost_price, selling_price, quantity, reorder_level, expiry_date):
        query = """
            INSERT INTO products (barcode, name, category, cost_price, selling_price, 
                                 quantity, reorder_level, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (barcode, name, category, cost_price, 
                                           selling_price, quantity, reorder_level, expiry_date))
    
    def get_all_products(self):
        query = "SELECT * FROM products ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_product_by_barcode(self, barcode):
        query = "SELECT * FROM products WHERE barcode = ?"
        return self.db.fetch_one(query, (barcode,))
    
    def get_product_by_id(self, product_id):
        query = "SELECT * FROM products WHERE id = ?"
        return self.db.fetch_one(query, (product_id,))
    
    def update_product(self, product_id, name, category, selling_price, reorder_level):
        query = """
            UPDATE products 
            SET name = ?, category = ?, selling_price = ?, reorder_level = ?
            WHERE id = ?
        """
        return self.db.execute_query(query, (name, category, selling_price, reorder_level, product_id))
    
    def update_stock(self, product_id, quantity_change):
        query = "UPDATE products SET quantity = quantity + ? WHERE id = ?"
        return self.db.execute_query(query, (quantity_change, product_id))
    
    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE id = ?"
        return self.db.execute_query(query, (product_id,))
    
    def get_low_stock_products(self):
        query = "SELECT * FROM products WHERE quantity <= reorder_level"
        return self.db.fetch_all(query)
    
    def search_products(self, search_term):
        query = "SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ? ORDER BY name"
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))

class CustomerModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_customer(self, name, phone, email, address=None):
        query = """
            INSERT INTO customers (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, phone, email, address))
    
    def get_all_customers(self):
        query = "SELECT * FROM customers ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_customer_by_id(self, customer_id):
        query = "SELECT * FROM customers WHERE id = ?"
        return self.db.fetch_one(query, (customer_id,))
    
    def get_customer_by_phone(self, phone):
        query = "SELECT * FROM customers WHERE phone = ?"
        return self.db.fetch_one(query, (phone,))
    
    def update_loyalty_points(self, customer_id, points):
        query = "UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?"
        return self.db.execute_query(query, (points, customer_id))
    
    def update_customer(self, customer_id, name, phone, email, address):
        query = """
            UPDATE customers 
            SET name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
        """
        return self.db.execute_query(query, (name, phone, email, address, customer_id))
    
    def delete_customer(self, customer_id):
        # Check if customer has sales
        check_query = "SELECT COUNT(*) as count FROM sales WHERE customer_id = ?"
        result = self.db.fetch_one(check_query, (customer_id,))
        if result and result['count'] > 0:
            return False  # Cannot delete customer with sales
        query = "DELETE FROM customers WHERE id = ?"
        self.db.execute_query(query, (customer_id,))
        return True
    
    def search_customers(self, search_term):
        query = "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name"
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))

class SaleModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_sale(self, invoice_number, user_id, customer_id, total_amount, discount, tax, payment_method, items):
        cursor = None
        try:
            if not self.db.connection:
                self.db.connect()
            
            cursor = self.db.connection.cursor()
            
            # Insert sale
            sale_query = """
                INSERT INTO sales (invoice_number, user_id, customer_id, total_amount, discount, tax, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sale_query, (invoice_number, user_id, customer_id, total_amount, discount, tax, payment_method))
            sale_id = cursor.lastrowid
            
            # Insert sale items
            for item in items:
                item_query = """
                    INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(item_query, (sale_id, item['product_id'], item['quantity'], 
                                          item['price'], item['subtotal']))
                
                # Update product stock
                stock_query = "UPDATE products SET quantity = quantity - ? WHERE id = ?"
                cursor.execute(stock_query, (item['quantity'], item['product_id']))
            
            self.db.connection.commit()
            return sale_id
        except Exception as e:
            print(f"Sale creation error: {e}")
            if self.db.connection:
                self.db.connection.rollback()
            return None
    
    def get_daily_sales(self, date=None):
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT s.*, u.username, c.name as customer_name 
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.created_at) = ?
            ORDER BY s.created_at DESC
        """
        return self.db.fetch_all(query, (date,))
    
    def get_sales_summary(self, start_date, end_date):
        query = """
            SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(SUM(discount), 0) as total_discount,
                COALESCE(SUM(tax), 0) as total_tax,
                COALESCE(AVG(total_amount), 0) as avg_transaction
            FROM sales
            WHERE DATE(created_at) BETWEEN ? AND ?
        """
        return self.db.fetch_one(query, (start_date, end_date))
    
    def get_sales_by_date_range(self, start_date, end_date, payment_method=None):
        query = """
            SELECT s.*, u.username as cashier_name, c.name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.created_at) BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if payment_method and payment_method != "All":
            query += " AND s.payment_method = ?"
            params.append(payment_method.lower())
        
        query += " ORDER BY s.created_at DESC"
        
        return self.db.fetch_all(query, params)
    
    def get_top_products(self, limit=5):
        query = """
            SELECT p.name, 
                   COALESCE(SUM(si.quantity), 0) as total_qty, 
                   COALESCE(SUM(si.subtotal), 0) as total_revenue
            FROM products p
            LEFT JOIN sale_items si ON p.id = si.product_id
            GROUP BY p.id
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (limit,))
