from datetime import date
from math import isfinite

FIELDNAMES = ["id", "date", "kind", "category", "amount", "currency"]

KINDS = {"income", "expense"}

CATEGORIES = {
    "food",
    "housing",
    "transport",
    "utilities",
    "entertainment",
    "salary",
    "other"
}


def validate_transaction(record):
    if set(record) != set(FIELDNAMES):
        raise ValueError(
            "Transaction must have exactly: " + ", ".join(FIELDNAMES)
        )

    identifier = str(record["id"]).strip()

    if not (identifier.startswith("T") and identifier[1:].isdigit()):
        raise ValueError("ID must look like T001")

    transaction_date = str(record["date"]).strip()

    try:
        parsed_date = date.fromisoformat(transaction_date)
    except ValueError:
        raise ValueError("Date must be YYYY-MM-DD")

    if parsed_date.isoformat() != transaction_date:
        raise ValueError("Date must be YYYY-MM-DD")

    kind = str(record["kind"]).strip().lower()

    if kind not in KINDS:
        raise ValueError("Kind must be income or expense")

    category = str(record["category"]).strip().lower()

    if category not in CATEGORIES:
        raise ValueError("Unknown category: " + category)

    try:
        amount = float(record["amount"])
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number")

    if not isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be a positive finite number")

    currency = str(record["currency"]).strip().upper()

    if currency != "EUR":
        raise ValueError("Release 1 supports EUR only")

    return {
        "id": identifier,
        "date": transaction_date,
        "kind": kind,
        "category": category,
        "amount": amount,
        "currency": currency
    }