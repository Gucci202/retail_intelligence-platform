
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

# Reproducible random data
random.seed(42)

NUM_CUSTOMERS = 2000
NUM_PRODUCTS = 100
NUM_ORDERS = 10000

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home",
    "Beauty",
    "Sports",
    "Accessories"
]

REGIONS = [
    "North",
    "South",
    "East",
    "West"
]


def generate_customers():
    customers = []

    for customer_id in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "customer_id": customer_id,
            "customer_name": f"Customer_{customer_id}",
            "region": random.choice(REGIONS)
        })

    return customers


def generate_products():
    products = []

    for product_id in range(1, NUM_PRODUCTS + 1):
        products.append({
            "product_id": product_id,
            "product_name": f"Product_{product_id}",
            "category": random.choice(CATEGORIES),
            "unit_price": round(random.uniform(5, 1000), 2)
        })

    return products


def generate_orders(customers, products):
    orders = []

    start_date = datetime(2024, 1, 1)

    for order_id in range(1, NUM_ORDERS + 1):
        customer = random.choice(customers)
        product = random.choice(products)

        order_date = start_date + timedelta(
            days=random.randint(0, 730)
        )

        quantity = random.randint(1, 5)

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "unit_price": product["unit_price"],
            "revenue": round(
                product["unit_price"] * quantity, 2
            )
        })

    return orders


def save_csv(filename, records):
    if not records:
        return

    filepath = DATA_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys()
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"Created {filepath} with {len(records)} records")


def main():
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers, products)

    save_csv("customers.csv", customers)
    save_csv("products.csv", products)
    save_csv("orders.csv", orders)

    print("\nRetail dataset generation completed!")


if __name__ == "__main__":
    main()
