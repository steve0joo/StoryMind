"""
Database Initialization Script
Creates SQLite database with tables for books, characters, and images
"""

import sqlite3
from datetime import datetime
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'storymind.db')

def init_database():
    """Initialize SQLite database with required tables"""

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating database tables...")

    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            upload_date TEXT,
            processing_status TEXT,
            faiss_index_path TEXT,
            character_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Books table created")

    # Characters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            name TEXT NOT NULL,
            canonical_description TEXT,
            seed INTEGER NOT NULL,
            mention_count INTEGER DEFAULT 0,
            relationships TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
    ''')
    print("✓ Characters table created")

    # Create index on book_id for faster character queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_characters_book_id
        ON characters (book_id)
    ''')

    # Images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            prompt TEXT,
            style TEXT,
            image_url TEXT,
            generation_time_ms INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
        )
    ''')
    print("✓ Images table created")

    # Create index on character_id for faster image queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_images_character_id
        ON images (character_id)
    ''')

    # Commit changes
    conn.commit()

    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(f"\n✅ Database initialized successfully at: {DB_PATH}")
    print(f"Tables created: {', '.join([t[0] for t in tables])}")

    conn.close()

def reset_database():
    """Drop all tables and recreate them (USE WITH CAUTION)"""

    if os.path.exists(DB_PATH):
        response = input(f"⚠️  This will delete {DB_PATH}. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Database reset cancelled.")
            return

        os.remove(DB_PATH)
        print("Old database deleted.")

    init_database()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()
