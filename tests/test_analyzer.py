import sqlite3
import tempfile
import unittest
from pathlib import Path
from src.analysis import analyze_jobs
from src.database import create_database, insert_jobs, load_jobs_from_csv


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'jobs.db'
        create_database(self.db)

    def test_sample_reports_and_repeat_import(self):
        jobs = load_jobs_from_csv()
        insert_jobs(jobs, self.db)
        insert_jobs(jobs, self.db)
        report = analyze_jobs(self.db)
        self.assertEqual(report['total_jobs'], 5)
        self.assertEqual(report['top_skills'][:2], [('Python', 5), ('SQL', 4)])
        self.assertEqual(report['locations'], [('Tokyo', 4), ('Osaka', 1)])
        self.assertEqual(len(report['matching_jobs']), 5)

    def test_exact_skill_and_duplicate_mentions(self):
        insert_jobs([
            dict(title='A', company='B', location='', skills=' Python,python,Pythonista, SQL '),
            dict(title='C', company='D', location='Tokyo', skills='Pythonista'),
        ], self.db)
        report = analyze_jobs(self.db, 'python')
        self.assertEqual(len(report['matching_jobs']), 1)
        self.assertIn(('Python', 1), report['top_skills'])
        self.assertIn(('Unknown', 1), report['locations'])
        self.assertEqual(analyze_jobs(self.db, "Python' OR 1=1 --")['matching_jobs'], [])

    def test_invalid_import_preserves_data(self):
        insert_jobs(load_jobs_from_csv(), self.db)
        for jobs in ([], [dict(title='', company='B', location='', skills='')], [{'title': 'A'}]):
            with self.assertRaises(ValueError):
                insert_jobs(jobs, self.db)
        self.assertEqual(analyze_jobs(self.db)['total_jobs'], 5)

    def test_malformed_csv(self):
        source = Path(self.temp.name) / 'bad.csv'
        for text in ('wrong,header\n', 'title,company,location,skills\nA,B,Tokyo,Python,SQL\n',
                     'title,company,location,skills\nA,B\n'):
            source.write_text(text)
            with self.assertRaises(ValueError):
                load_jobs_from_csv(source)

    def test_transaction_rollback(self):
        insert_jobs(load_jobs_from_csv(), self.db)
        with sqlite3.connect(self.db) as connection:
            connection.execute("CREATE TRIGGER reject_job BEFORE INSERT ON jobs BEGIN SELECT RAISE(ABORT, 'rejected'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            insert_jobs(load_jobs_from_csv(), self.db)
        self.assertEqual(analyze_jobs(self.db)['total_jobs'], 5)


if __name__ == '__main__':
    unittest.main()
