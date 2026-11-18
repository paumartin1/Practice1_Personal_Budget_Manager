import argparse
import sys

from datetime import date
from pathlib import Path

from .services import add_transaction, summarize
from .storage import (
    load_transactions,
    save_transactions,
    backup_transactions
)
from .validation import CATEGORIES


DEFAULT_DATA = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "transactions.csv"
)


def show_transactions(transactions):
    if not transactions:
        print("No transactions yet.")
        return

    for transaction in transactions:
        print(
            f'{transaction["id"]} | '
            f'{transaction["date"]} | '
            f'{transaction["kind"]} | '
            f'{transaction["category"]} | '
            f'{transaction["amount"]:.2f} EUR'
        )


def show_summary(transactions):
    summary = summarize(transactions)

    print("FINANCIAL SUMMARY")
    print(f'Total Income: {summary["total_income"]:.2f} EUR')
    print(f'Total Expenses: {summary["total_expenses"]:.2f} EUR')
    print(f'Current Balance: {summary["balance"]:.2f} EUR')
    print("Expenses by Category:")

    for category, amount in summary["expenses_by_category"].items():
        print(f"  {category}: {amount:.2f} EUR")


def execute(
    command,
    data_file,
    transaction_date=None,
    kind=None,
    category=None,
    amount=None,
    destination=None
):
    try:
        transactions = load_transactions(data_file)

        if command == "add":
            updated = add_transaction(
                transactions,
                transaction_date,
                kind,
                category,
                amount
            )

            save_transactions(data_file, updated)
            print(f'Transaction saved: {updated[-1]["id"]}')

        elif command == "list":
            show_transactions(transactions)

        elif command == "summary":
            show_summary(transactions)

        elif command == "backup":
            backup_path = backup_transactions(data_file, destination)
            print(f"Backup verified: {backup_path}")

        return 0

    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def interactive_menu(data_file):
    while True:
        print("\n=== PERSONAL BUDGET MANAGER ===")
        print("1. Add transaction")
        print("2. List transactions")
        print("3. Financial summary")
        print("4. Create backup")
        print("0. Exit")

        try:
            choice = input("Select an option: ").strip()

            if choice == "0":
                print("Goodbye!")
                return 0

            elif choice == "1":
                transaction_date = input("Date (YYYY-MM-DD): ").strip()
                kind = input("Kind (income/expense): ").strip()
                category = input("Category: ").strip()
                amount = input("Amount: ").strip()

                execute(
                    "add",
                    data_file,
                    transaction_date,
                    kind,
                    category,
                    amount
                )

            elif choice == "2":
                execute("list", data_file)

            elif choice == "3":
                execute("summary", data_file)

            elif choice == "4":
                execute("backup", data_file)

            else:
                print("Invalid option. Choose 0, 1, 2, 3 or 4.")

        except (EOFError, KeyboardInterrupt):
            print("\nExited.")
            return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        return interactive_menu(DEFAULT_DATA)

    parser = argparse.ArgumentParser(
        description="Personal Budget Manager"
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="CSV file to use"
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True
    )

    add_parser = commands.add_parser(
        "add",
        help="Add a transaction"
    )

    add_parser.add_argument("amount")

    add_parser.add_argument(
        "--kind",
        choices=["income", "expense"],
        required=True
    )

    add_parser.add_argument(
        "--category",
        choices=sorted(CATEGORIES),
        required=True
    )

    add_parser.add_argument(
        "--date",
        default=date.today().isoformat()
    )

    commands.add_parser("list")
    commands.add_parser("summary")

    backup_parser = commands.add_parser("backup")
    backup_parser.add_argument(
        "destination",
        nargs="?",
        type=Path
    )

    args = parser.parse_args(argv)

    return execute(
        args.command,
        args.data,
        transaction_date=getattr(args, "date", None),
        kind=getattr(args, "kind", None),
        category=getattr(args, "category", None),
        amount=getattr(args, "amount", None),
        destination=getattr(args, "destination", None)
    )


if __name__ == "__main__":
    sys.exit(main())