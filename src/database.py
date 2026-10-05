import sqlite3


def create_database():
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            skills TEXT
        )
    """)
    connection.commit()
    connection.close()
