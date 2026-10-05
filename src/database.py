import csv
import sqlite3


DB_NAME = "jobs.db"
CSV_FILE = "data/jobs.csv"


def create_database():
    connection = sqlite3.connect(DB_NAME)
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


def load_jobs_from_csv():
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def insert_jobs(jobs):
    connection = sqlite3.connect(DB_NAME)
    try:
        with connection:
            # Replace the sample dataset so repeated runs do not duplicate jobs.
            connection.execute("DELETE FROM jobs")
            for job in jobs:
                connection.execute("""
                    INSERT INTO jobs (title, company, location, skills)
                    VALUES (?, ?, ?, ?)
                """, (
                    job["title"],
                    job["company"],
                    job["location"],
                    job["skills"],
                ))
    finally:
        connection.close()
