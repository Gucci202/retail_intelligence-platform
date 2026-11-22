
import csv
from pathlib import Path
from decimal import Decimal
from database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def read_csv(filename):
    filepath = DATA_DIR / filename

    with open(filepath, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def import_data():
    customers = read_csv("customers.csv")
    products = read_csv("products.csv")
    orders = read_csv("orders.csv")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        connection.start_transaction()

        # Import customers
        for customer in customers:
            cursor.execute(
                """
                INSERT INTO customers
                (customer_id, customer_name, region)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    customer_name = VALUES(customer_name),
                    region = VALUES(region)
                """,
                (
                    int(customer["customer_id"]),
                    customer["customer_name"],
                    customer["region"]
                )
            )

        # Import products
        for product in products:
            cursor.execute(
                """
                INSERT INTO products
                (product_id, product_name, category, unit_price)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    product_name = VALUES(product_name),
                    category = VALUES(category),
                    unit_price = VALUES(unit_price)
                """,
                (
                    int(product["product_id"]),
                    product["product_name"],
                    product["category"],
                    Decimal(product["unit_price"])
                )
            )

        # Import orders
        for order in orders:
            cursor.execute(
                """
                INSERT INTO orders
                (order_id, customer_id, product_id,
                 order_date, quantity, unit_price, revenue)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    customer_id = VALUES(customer_id),
                    product_id = VALUES(product_id),
                    order_date = VALUES(order_date),
                    quantity = VALUES(quantity),
                    unit_price = VALUES(unit_price),
                    revenue = VALUES(revenue)
                """,
                (
                    int(order["order_id"]),
                    int(order["customer_id"]),
                    int(order["product_id"]),
                    order["order_date"],
                    int(order["quantity"]),
                    Decimal(order["unit_price"]),
                    Decimal(order["revenue"])
                )
            )

        connection.commit()
        print("Import successful!")

        for table in ("customers", "products", "orders"):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count:,} records")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    import_data()
