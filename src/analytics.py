## calculates first business metrics

from collections import defaultdict
from decimal import Decimal



def calculate_kpis(transactions):
    total_revenue = calculate_total_revenue(transactions)
    count = len(transactions)

    return {
        "total_revenue": total_revenue,
        "total_transactions": count,
        "total_units_sold": sum(
            row["quantity"] for row in transactions
        ),
        "average_transaction_value": (
            total_revenue / count if count else Decimal("0")
        )
    }






def calculate_total_revenue(transactions):
    return sum(
        (row["revenue"] for row in transactions),
        Decimal("0")
    )


def revenue_by_product(transactions):
    totals = defaultdict(lambda: Decimal("0"))

    for row in transactions:
        totals[row["product"]] += row["revenue"]

    return dict(totals)


def revenue_by_category(transactions):
    totals = defaultdict(lambda: Decimal("0"))

    for row in transactions:
        totals[row["category"]] += row["revenue"]

    return dict(totals)


def calculate_kpis(transactions):
    total_revenue = calculate_total_revenue(transactions)
    count = len(transactions)

    return {
        "total_revenue": total_revenue,
        "total_transactions": count,
        "total_units_sold": sum(
            row["quantity"] for row in transactions
        ),
        "average_transaction_value": (
            total_revenue / count if count else Decimal("0")
        )
    }
