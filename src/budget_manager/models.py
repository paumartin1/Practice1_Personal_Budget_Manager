from .validation import validate_transaction


def make_transaction(identifier, transaction_date, kind, category, amount):
    transaction = {
        "id": identifier,
        "date": transaction_date,
        "kind": kind,
        "category": category,
        "amount": amount,
        "currency": "EUR"
    }

    return validate_transaction(transaction)