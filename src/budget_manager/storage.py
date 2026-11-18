import csv
import hashlib
from datetime import datetime
from pathlib import Path

from .validation import FIELDNAMES, validate_transaction


def load_transactions(path):
    path = Path(path)

    if not path.exists():
        return []

    transactions = []
    identifiers = set()

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDNAMES:
            raise ValueError("CSV header must be: " + ",".join(FIELDNAMES))

        for line_number, row in enumerate(reader, start=2):
            try:
                transaction = validate_transaction(row)
            except ValueError as error:
                raise ValueError(f"Row {line_number}: {error}") from error

            if transaction["id"] in identifiers:
                raise ValueError(f"Row {line_number}: duplicate transaction id")

            identifiers.add(transaction["id"])
            transactions.append(transaction)

    return transactions


def save_transactions(path, transactions):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_name(path.name + ".tmp")

    with temp_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for transaction in transactions:
            writer.writerow(validate_transaction(transaction))

    temp_path.replace(path)


def backup_transactions(source_path, destination=None):
    source_path = Path(source_path)

    if not source_path.is_file():
        raise ValueError("No transaction file exists to back up")

    if destination is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        destination = (
            source_path.parent.parent
            / "backups"
            / f"transactions_{timestamp}.csv"
        )

    destination = Path(destination)

    if source_path.resolve() == destination.resolve():
        raise ValueError("Backup destination must differ from source")

    destination.parent.mkdir(parents=True, exist_ok=True)

    original_bytes = source_path.read_bytes()

    with destination.open("xb") as file:
        file.write(original_bytes)

    source_hash = hashlib.sha256(original_bytes).hexdigest()
    backup_hash = hashlib.sha256(destination.read_bytes()).hexdigest()

    if source_hash != backup_hash or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("Backup verification failed")

    return destination