# Job Market Skills Analyzer

A small Python + SQLite project that imports job postings from CSV and reports which skills and locations appear most often.

**The included dataset contains five fictional jobs. These results demonstrate the code, not actual job-market demand.**

## Run

Requires Python 3.10 or later. No third-party packages are needed.

```bash
git clone https://github.com/sattaruavikshit/job-market-skills-analyzer.git
cd job-market-skills-analyzer
python3 main.py
```

On Windows, use `python` instead of `python3` if needed.

The default sample reports Python in 5 jobs (100%), SQL in 4 (80%), Tokyo with 4 jobs, and Osaka with 1.

```bash
python3 main.py --skill SQL --top 5
python3 main.py --csv data/jobs.csv --db jobs.db
python3 -m unittest discover -s tests -v
```

Default file paths are relative to the project directory, so the script also works when called from another directory. Explicit `--csv` and `--db` paths are relative to your current working directory. Each run replaces the database's imported dataset; it does not append jobs. Validation happens before replacement, and database errors roll back the import.

## Data format

Use this exact header. Quote the skills field because it contains commas:

```csv
title,company,location,skills
Data Analyst,Example Company,Tokyo,"Python,SQL,Excel"
```

Title and company are required. Location and skills may be empty. Blank locations appear as `Unknown` in the report. Empty or malformed datasets are rejected to protect existing data. Each CSV row represents one posting; duplicate postings in the CSV are counted separately.

## How it works

1. `src/database.py` reads rows with `csv.DictReader`, validates them, and uses parameterized SQL to insert them.
2. `jobs` stores posting details. `job_skills` stores one row per distinct skill per job, allowing SQL to count exact skills rather than substring matches.
3. `src/analysis.py` uses `GROUP BY`, `COUNT`, and a `JOIN` to report skill frequency, locations, and jobs requiring a selected skill.
4. `main.py` prints the reports and accepts command-line options.

Skill matching ignores case and surrounding whitespace. Repeated mentions within one posting count once. Aliases such as `ML` and `Machine Learning` remain separate. Percentages use all imported postings as the denominator and can add up to more than 100% because jobs require multiple skills.

## Try SQL yourself

After running the program, open `sqlite3 jobs.db` if the SQLite command-line tool is installed:

```sql
SELECT title, company FROM jobs WHERE location = 'Tokyo';

SELECT skill, COUNT(*) AS job_count
FROM job_skills
GROUP BY skill COLLATE NOCASE
ORDER BY job_count DESC, skill COLLATE NOCASE;
```

Exit with `.quit`. Generated databases are ignored by Git; the CSV and code reproduce them.

## Scope and future data

This version completes CSV import and basic SQL analysis. It does not scrape job websites or infer trends from five fictional rows. For meaningful market analysis, replace the CSV with permitted real postings, document their source and collection date, remove duplicate postings, and standardize skill aliases. Salary analysis and time trends need additional fields and data.
