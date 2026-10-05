"""SQL reports count job postings, not repeated mentions within a posting."""
import sqlite3
from src.database import DB_NAME


def analyze_jobs(db_path=DB_NAME, skill="Python", limit=10):
    connection = sqlite3.connect(db_path)
    try:
        total = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        skills = connection.execute("""
            SELECT skill, COUNT(*) AS job_count
            FROM job_skills GROUP BY skill COLLATE NOCASE
            ORDER BY job_count DESC, skill COLLATE NOCASE LIMIT ?
        """, (limit,)).fetchall()
        locations = connection.execute("""
            SELECT COALESCE(NULLIF(location, ''), 'Unknown'), COUNT(*) AS job_count
            FROM jobs GROUP BY COALESCE(NULLIF(location, ''), 'Unknown')
            ORDER BY job_count DESC, 1
        """).fetchall()
        matching = connection.execute("""
            SELECT jobs.title, jobs.company, jobs.location
            FROM jobs JOIN job_skills ON jobs.id = job_skills.job_id
            WHERE job_skills.skill = ? COLLATE NOCASE
            ORDER BY jobs.title, jobs.company
        """, (skill.strip(),)).fetchall()
        return {"total_jobs": total, "top_skills": skills,
                "locations": locations, "matching_jobs": matching}
    finally:
        connection.close()
