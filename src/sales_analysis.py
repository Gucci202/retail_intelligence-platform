import csv

with open("data/retail_sales.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for transaction in reader:
        print(transaction)