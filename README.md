
# Personal Budget Manager

Practice 1 - Programming with Python

## Description

A Python application for managing personal income and expenses.

The application allows users to add transactions, display existing records, calculate financial summaries and create backups.

Transactions are stored in a CSV file.

## Requirements

- Python 3.10 or later
- No external libraries required

## How to run

Open a terminal in the project folder.

Interactive menu:

```bash
python run.py
```

Display the available commands:

```bash
python run.py --help
```

Add an expense:

```bash
python run.py add 18.50 --kind expense --category food
```

Display transactions:

```bash
python run.py list
```

Show the financial summary:

```bash
python run.py summary
```

Create a backup:

```bash
python run.py backup
```

## Sample data

Example transactions are available in:

`data/sample_transactions.csv`

To calculate their summary:

```bash
python run.py --data data/sample_transactions.csv summary
```



## Tests

Run the automated tests:

```bash
python -m unittest discover -s tests -v
```

The tests cover normal transactions, invalid input, empty data, duplicate IDs, CSV persistence and backups.

## Validation

The program checks transaction dates, amounts, categories and transaction types.

Amounts must be positive, and transactions must use EUR.

## Known limitations

- Only EUR is supported.
- Transactions cannot be edited or deleted.
- Categories are predefined.
- Concurrent modification of the same CSV is not supported.
- Amounts use float, which can introduce rounding errors in financial calculations.

## Project structure

Business logic, validation, storage and CLI functions are implemented in separate modules.
