import tempfile
import unittest

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from src.budget_manager.cli import main
from src.budget_manager.models import make_transaction
from src.budget_manager.services import add_transaction, summarize
from src.budget_manager.storage import (
    backup_transactions,
    load_transactions,
    save_transactions
)


class BudgetManagerTests(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

        self.path = Path(self.folder.name) / "transactions.csv"

        self.first = make_transaction(
            "T001", "2026-11-10", "income", "salary", 100.0
        )

        self.second = make_transaction(
            "T002", "2026-11-11", "expense", "food", 18.50
        )

    def test_normal_balance_and_categories(self):
        result = summarize([self.first, self.second])

        self.assertAlmostEqual(result["total_income"], 100.0)
        self.assertAlmostEqual(result["total_expenses"], 18.5)
        self.assertAlmostEqual(result["balance"], 81.5)
        self.assertEqual(
            result["expenses_by_category"],
            {"food": 18.5}
        )

    def test_empty_budget(self):
        self.assertEqual(summarize([])["balance"], 0)
        self.assertEqual(load_transactions(self.path), [])

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-11-11", "expense", "food", -10
            )

    def test_zero_amount(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-11-11", "expense", "food", 0
            )

    def test_unknown_category(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-11-11", "expense", "games", 10
            )

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-02-30", "expense", "food", 10
            )

    def test_invalid_kind(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-11-11", "payment", "food", 10
            )

    def test_nan_amount(self):
        with self.assertRaises(ValueError):
            make_transaction(
                "T003", "2026-11-11", "expense", "food", "nan"
            )

    def test_save_and_reload(self):
        original = [self.first, self.second]

        save_transactions(self.path, original)
        loaded = load_transactions(self.path)

        self.assertEqual(original, loaded)
        self.assertTrue(self.path.exists())

    def test_add_transaction(self):
        initial = [self.first]

        updated = add_transaction(
            initial, "2026-11-12", "expense", "food", 5
        )

        self.assertEqual(len(initial), 1)
        self.assertEqual(len(updated), 2)
        self.assertEqual(updated[-1]["id"], "T002")

    def test_duplicate_ids(self):
        self.path.write_text(
            "id,date,kind,category,amount,currency\n"
            "T001,2026-11-11,expense,food,10,EUR\n"
            "T001,2026-11-12,expense,food,12,EUR\n",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_transactions(self.path)

    def test_invalid_csv_row(self):
        self.path.write_text(
            "id,date,kind,category,amount,currency\n"
            "T001,2026-11-11,expense,food,-5,EUR\n",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_transactions(self.path)

    def test_cli_add_and_summary(self):
        output = StringIO()

        with redirect_stdout(output):
            code1 = main([
                "--data", str(self.path),
                "add", "18.50",
                "--kind", "expense",
                "--category", "food",
                "--date", "2026-11-18"
            ])

            code2 = main([
                "--data", str(self.path),
                "summary"
            ])

        self.assertEqual(code1, 0)
        self.assertEqual(code2, 0)
        self.assertIn("Total Expenses: 18.50 EUR", output.getvalue())

    def test_cli_invalid_amount(self):
        errors = StringIO()

        with redirect_stderr(errors):
            code = main([
                "--data", str(self.path),
                "add", "-3",
                "--kind", "expense",
                "--category", "food"
            ])

        self.assertEqual(code, 1)
        self.assertIn("positive finite", errors.getvalue())

    def test_backup(self):
        save_transactions(self.path, [self.first])

        backup_path = Path(self.folder.name) / "backup.csv"

        result = backup_transactions(self.path, backup_path)

        self.assertEqual(result.read_bytes(), self.path.read_bytes())

        with self.assertRaises(FileExistsError):
            backup_transactions(self.path, backup_path)


if __name__ == "__main__":
    unittest.main()