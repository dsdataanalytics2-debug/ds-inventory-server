"""
Database Migration Script for Enhanced Inventory System
This script migrates from the old schema (quantity-only) to the new schema (quantity + pricing)
"""

import sqlite3
import os
from decimal import Decimal

def migrate_database():
    """
    Migrate existing database to new schema with pricing fields
    """
    db_path = "inventory.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("No existing database found. New database will be created with enhanced schema.")
        return
    
    print("Starting database migration...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'total_added_amount' in columns:
            print("Database already migrated. No action needed.")
            return
        
        print("Old schema detected. Starting migration...")
        
        # Backup existing data
        print("1. Backing up existing data...")
        
        # Backup products
        cursor.execute("SELECT * FROM products")
        old_products = cursor.fetchall()
        
        # Backup add_history
        cursor.execute("SELECT * FROM add_history")
        old_add_history = cursor.fetchall()
        
        # Backup sell_history
        cursor.execute("SELECT * FROM sell_history")
        old_sell_history = cursor.fetchall()
        
        # Drop old tables
        print("2. Dropping old tables...")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS add_history")
        cursor.execute("DROP TABLE IF EXISTS sell_history")
        
        # Create new tables with enhanced schema
        print("3. Creating new tables with enhanced schema...")
        
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                total_added_qty INTEGER DEFAULT 0,
                total_added_amount DECIMAL(10,2) DEFAULT 0.00,
                total_sold_qty INTEGER DEFAULT 0,
                total_sold_amount DECIMAL(10,2) DEFAULT 0.00,
                available_stock INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE add_history (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                total_amount DECIMAL(10,2),
                date TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE sell_history (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                total_amount DECIMAL(10,2),
                date TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Migrate products data
        print("4. Migrating products data...")
        default_price = Decimal('1.00')  # Default price for existing data
        
        for product in old_products:
            # Old schema: id, name, total_added, total_sold, available_stock
            id, name, total_added, total_sold, available_stock = product
            
            # Calculate amounts with default price
            total_added_amount = float(Decimal(str(total_added)) * default_price)
            total_sold_amount = float(Decimal(str(total_sold)) * default_price)
            
            cursor.execute("""
                INSERT INTO products 
                (id, name, total_added_qty, total_added_amount, total_sold_qty, total_sold_amount, available_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id, name, total_added, total_added_amount, total_sold, total_sold_amount, available_stock))
        
        # Migrate add_history data
        print("5. Migrating add_history data...")
        for record in old_add_history:
            # Old schema: id, product_id, quantity, date
            id, product_id, quantity, date = record
            unit_price = float(default_price)
            total_amount = float(Decimal(str(quantity)) * default_price)
            
            cursor.execute("""
                INSERT INTO add_history 
                (id, product_id, quantity, unit_price, total_amount, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id, product_id, quantity, unit_price, total_amount, date))
        
        # Migrate sell_history data
        print("6. Migrating sell_history data...")
        for record in old_sell_history:
            # Old schema: id, product_id, quantity, date
            id, product_id, quantity, date = record
            unit_price = float(default_price)
            total_amount = float(Decimal(str(quantity)) * default_price)
            
            cursor.execute("""
                INSERT INTO sell_history 
                (id, product_id, quantity, unit_price, total_amount, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id, product_id, quantity, unit_price, total_amount, date))
        
        # Commit changes
        conn.commit()
        print("7. Migration completed successfully!")
        print(f"   - Migrated {len(old_products)} products")
        print(f"   - Migrated {len(old_add_history)} add history records") 
        print(f"   - Migrated {len(old_sell_history)} sell history records")
        print(f"   - Default price of ৳{default_price} was used for existing records")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
