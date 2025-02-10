import sqlite3


def initialize_db():
    conn = sqlite3.connect("party_monitor.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brother TEXT NOT NULL,
            year TEXT,
            gender TEXT,
            campus_status TEXT,
            check_in_time DATETIME,
            check_in_status TEXT DEFAULT 'Not Checked In'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brothers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            year TEXT
        )
    """)

    conn.commit()
    conn.close()
