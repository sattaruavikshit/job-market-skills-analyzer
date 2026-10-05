"""Validate CSV data and store jobs and individual skills in SQLite."""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_NAME = ROOT / "jobs.db"
CSV_FILE = ROOT / "data/jobs.csv"
FIELDS = ("title", "company", "location", "skills")


def create_database(db_path=DB_NAME):
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    skills TEXT
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS job_skills (
                    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                    skill TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (job_id, skill)
                )
            """)
    finally:
        connection.close()


def validate_jobs(jobs):
    """Reject invalid rows before replacing any existing data."""
    cleaned = []
    for number, row in enumerate(jobs, start=2):
        if any(not isinstance(row.get(field), str) for field in FIELDS):
            raise ValueError(f"CSV row {number}: expected all four columns.")
        job = {field: row[field].strip() for field in FIELDS}
        if not job["title"] or not job["company"]:
            raise ValueError(f"CSV row {number}: title and company are required.")
        cleaned.append(job)
    if not cleaned:
        raise ValueError("CSV contains no jobs; existing data has been preserved.")
    return cleaned


def load_jobs_from_csv(csv_path=CSV_FILE):
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("CSV header must be title,company,location,skills.")
        rows = []
        for number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {number}: extra columns; quote comma-separated skills.")
            rows.append(row)
        return validate_jobs(rows)


def insert_jobs(jobs, db_path=DB_NAME):
    jobs = validate_jobs(jobs)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.execute("DELETE FROM job_skills")
            connection.execute("DELETE FROM jobs")
            for job in jobs:
                cursor = connection.execute("""
                    INSERT INTO jobs (title, company, location, skills)
                    VALUES (?, ?, ?, ?)
                """, tuple(job[field] for field in FIELDS))
                # Each job counts once per skill, ignoring case and whitespace.
                skills = {}
                for value in job["skills"].split(","):
                    skill = value.strip()
                    if skill:
                        skills.setdefault(skill.casefold(), skill)
                connection.executemany(
                    "INSERT INTO job_skills (job_id, skill) VALUES (?, ?)",
                    [(cursor.lastrowid, skill) for skill in skills.values()],
                )
    finally:
        connection.close()
