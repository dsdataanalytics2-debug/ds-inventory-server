"""
Database migration script to create the orders table
Run this script to add the orders table to existing database
"""

import sqlite3
from datetime import datetime

def create_orders_table():
    """Create orders table if it doesn't exist"""
    try:
        # Connect to database
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='orders'
        """)
        
        if cursor.fetchone():
            print("✅ Orders table already exists")
            conn.close()
            return
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity_sold INTEGER NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                customer_name TEXT,
                customer_address TEXT,
                customer_phone TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        conn.commit()
        print("✅ Orders table created successfully!")
        
        # Verify table creation
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='orders'
        """)
        
        table_schema = cursor.fetchone()
        if table_schema:
            print("\n📋 Table Schema:")
            print(table_schema[0])
        
        conn.close()
        print("\n✨ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating orders table: {str(e)}")
        raise

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("-" * 50)
    create_orders_table()
