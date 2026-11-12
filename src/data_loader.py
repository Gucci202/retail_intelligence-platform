##module that reads csv transaction and returns a list of dictionaries
import csv
from pathlib import Path


def load_sales(filepath):
    transactions = []

    with open(filepath, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transactions.append(row)

    return transactions
