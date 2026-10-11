import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "cafe_system.db"

@contextmanager
def database_connection():
    """Provides a safe database connection context manager."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

def setup_database():
    """Creates the necessary database tables for the Cafe Ordering System."""
    with database_connection() as connection:
        # 1. Enable foreign key constraints in SQLite
        connection.execute("PRAGMA foreign_keys = ON;")
        
        # 2. Create le Menu Items table (Stores products like coffee, pastries)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL CHECK (price >= 0)
            )
        """)
        
        # 3. Creates le Orders table (Stores customer orders)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                total_price REAL NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES menu_items (id) ON DELETE CASCADE
            )
        """)
        print("Database initialized successfully with cafe tables!")

# Automatically run the table setup when this file is imported
setup_database()