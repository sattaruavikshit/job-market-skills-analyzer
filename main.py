from src.database import create_database, load_jobs_from_csv, insert_jobs


def main():
    create_database()
    jobs = load_jobs_from_csv()
    insert_jobs(jobs)
    print(f"Successfully inserted {len(jobs)} jobs into the database.")


if __name__ == "__main__":
    main()
