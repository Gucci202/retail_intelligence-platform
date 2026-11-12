
import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ["DB_PASSWORD"],
        database="retail_intelligence"
    )


def insert_sales(transactions):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO sales (
            transaction_id,
            product,
            category,
            unit_price,
            quantity,
            revenue
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            product = VALUES(product),
            category = VALUES(category),
            unit_price = VALUES(unit_price),
            quantity = VALUES(quantity),
            revenue = VALUES(revenue)
    """

    try:
        for row in transactions:
            values = (
                row["transaction_id"],
                row["product"],
                row["category"],
                row["unit_price"],
                row["quantity"],
                row["revenue"]
            )

            cursor.execute(query, values)

        connection.commit()
        print(f"Successfully processed {len(transactions)} transactions!")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
