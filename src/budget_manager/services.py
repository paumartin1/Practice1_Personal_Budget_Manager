from .models import make_transaction


def add_transaction(transactions, transaction_date, kind, category, amount):
    existing_numbers = []

    for transaction in transactions:
        number = int(transaction["id"][1:])
        existing_numbers.append(number)

    next_number = max(existing_numbers, default=0) + 1

    new_transaction = make_transaction(
        f"T{next_number:03d}",
        transaction_date,
        kind,
        category,
        amount
    )

    return transactions + [new_transaction]


def summarize(transactions):
    total_income = 0.0
    total_expenses = 0.0
    expenses_by_category = {}

    for transaction in transactions:
        amount = transaction["amount"]

        if transaction["kind"] == "income":
            total_income += amount

        else:
            total_expenses += amount
            category = transaction["category"]

            expenses_by_category[category] = (
                expenses_by_category.get(category, 0) + amount
            )

    balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "expenses_by_category": expenses_by_category
    }