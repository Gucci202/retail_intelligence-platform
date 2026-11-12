
from decimal import Decimal, InvalidOperation


def clean_sales(transactions):
    cleaned = []
    rejected = []

    for row in transactions:
        try:
            transaction_id = int(row["transaction_id"])
            product = row["product"].strip()
            category = row["category"].strip()
            price = Decimal(row["unit_price"])
            quantity = int(row["quantity"])

            if not product or not category:
                raise ValueError("Missing product or category")

            if not price.is_finite() or price < 0 or quantity <= 0:
                raise ValueError("Invalid price or quantity")

            cleaned.append({
                "transaction_id": transaction_id,
                "product": product,
                "category": category,
                "unit_price": price,
                "quantity": quantity,
                "revenue": price * quantity
            })

        except (ValueError, KeyError, TypeError, InvalidOperation) as error:
            rejected.append({
                "row": row,
                "reason": str(error)
            })

    return cleaned, rejected
