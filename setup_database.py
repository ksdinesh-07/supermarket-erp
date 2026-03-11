import pymysql
from config import DB_CONFIG

def setup_database():
    try:
        # Connect without database to create it
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        
        cursor = connection.cursor()
        
        # Read and execute schema.sql
        with open('database/schema.sql', 'r') as file:
            sql_commands = file.read().split(';')
            
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
                    
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Database setup completed successfully!")
        print("Default admin credentials:")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    setup_database()
