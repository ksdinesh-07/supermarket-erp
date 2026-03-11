import hashlib
from datetime import datetime
from database.connection import DatabaseConnection

class UserModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def authenticate(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
        user = self.db.fetch_one(query, (username, password_hash))
        
        if user:
            # Update last login
            update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            self.db.execute_query(update_query, (user['id'],))
        
        return user
    
    def create_user(self, username, password, full_name, role):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = """
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s)
        """
        return self.db.execute_query(query, (username, password_hash, full_name, role))
    
    def get_all_users(self):
        query = "SELECT id, username, full_name, role, created_at, last_login FROM users"
        return self.db.fetch_all(query)
    
    def update_user(self, user_id, full_name, role):
        query = "UPDATE users SET full_name = %s, role = %s WHERE id = %s"
        return self.db.execute_query(query, (full_name, role, user_id))
    
    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = %s"
        return self.db.execute_query(query, (user_id,))

class ProductModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_product(self, barcode, name, category, cost_price, selling_price, quantity, reorder_level, expiry_date):
        query = """
            INSERT INTO products (barcode, name, category, cost_price, selling_price, 
                                 quantity, reorder_level, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (barcode, name, category, cost_price, 
                                           selling_price, quantity, reorder_level, expiry_date))
    
    def get_all_products(self):
        query = "SELECT * FROM products ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_product_by_barcode(self, barcode):
        query = "SELECT * FROM products WHERE barcode = %s"
        return self.db.fetch_one(query, (barcode,))
    
    def update_product(self, product_id, name, category, selling_price, reorder_level):
        query = """
            UPDATE products 
            SET name = %s, category = %s, selling_price = %s, reorder_level = %s
            WHERE id = %s
        """
        return self.db.execute_query(query, (name, category, selling_price, reorder_level, product_id))
    
    def update_stock(self, product_id, quantity_change):
        query = "UPDATE products SET quantity = quantity + %s WHERE id = %s"
        return self.db.execute_query(query, (quantity_change, product_id))
    
    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE id = %s"
        return self.db.execute_query(query, (product_id,))
    
    def get_low_stock_products(self):
        query = "SELECT * FROM products WHERE quantity <= reorder_level"
        return self.db.fetch_all(query)

class CustomerModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_customer(self, name, phone, email):
        query = """
            INSERT INTO customers (name, phone, email)
            VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (name, phone, email))
    
    def get_all_customers(self):
        query = "SELECT * FROM customers ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_customer_by_phone(self, phone):
        query = "SELECT * FROM customers WHERE phone = %s"
        return self.db.fetch_one(query, (phone,))
    
    def update_loyalty_points(self, customer_id, points):
        query = "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE id = %s"
        return self.db.execute_query(query, (points, customer_id))

class SaleModel:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_sale(self, invoice_number, user_id, customer_id, total_amount, discount, tax, items):
        cursor = None
        try:
            if not self.db.connection:
                self.db.connect()
            
            cursor = self.db.connection.cursor()
            
            # Insert sale
            sale_query = """
                INSERT INTO sales (invoice_number, user_id, customer_id, total_amount, discount, tax)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sale_query, (invoice_number, user_id, customer_id, total_amount, discount, tax))
            sale_id = cursor.lastrowid
            
            # Insert sale items
            for item in items:
                item_query = """
                    INSERT INTO sale_items (sale_id, product_id, quantity, price, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(item_query, (sale_id, item['product_id'], item['quantity'], 
                                          item['price'], item['subtotal']))
                
                # Update product stock
                stock_query = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
                cursor.execute(stock_query, (item['quantity'], item['product_id']))
            
            self.db.connection.commit()
            return sale_id
        except Exception as e:
            print(f"Sale creation error: {e}")
            if self.db.connection:
                self.db.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_daily_sales(self, date=None):
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT s.*, u.username, c.name as customer_name 
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.created_at) = %s
            ORDER BY s.created_at DESC
        """
        return self.db.fetch_all(query, (date,))
    
    def get_sales_summary(self, start_date, end_date):
        query = """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(total_amount) as total_revenue,
                SUM(discount) as total_discount,
                SUM(tax) as total_tax,
                AVG(total_amount) as avg_transaction
            FROM sales
            WHERE DATE(created_at) BETWEEN %s AND %s
        """
        return self.db.fetch_one(query, (start_date, end_date))
