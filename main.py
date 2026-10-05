"""Import a job CSV and print skill and location reports."""
import argparse
import sqlite3
from src.analysis import analyze_jobs
from src.database import DB_NAME, CSV_FILE, create_database, load_jobs_from_csv, insert_jobs


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=CSV_FILE, help="CSV file to import")
    parser.add_argument("--db", default=DB_NAME, help="SQLite database path")
    parser.add_argument("--skill", default="Python", help="Exact skill to search (case insensitive)")
    parser.add_argument("--top", type=positive_integer, default=10, help="Number of top skills")
    args = parser.parse_args()
    try:
        jobs = load_jobs_from_csv(args.csv)
        create_database(args.db)
        insert_jobs(jobs, args.db)
        report = analyze_jobs(args.db, args.skill, args.top)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Successfully inserted {len(jobs)} jobs into the database.")
    print("\nTop skills (jobs requiring each skill):")
    for skill, count in report["top_skills"]:
        print(f"  {skill}: {count} ({count / report['total_jobs']:.0%})")
    print("\nJobs by location:")
    for location, count in report["locations"]:
        print(f"  {location}: {count}")
    print(f"\nJobs requiring {args.skill.strip()}: {len(report['matching_jobs'])}")
    for title, company, location in report["matching_jobs"]:
        print(f"  {title} | {company} | {location or 'Unknown'}")


if __name__ == "__main__":
    main()
