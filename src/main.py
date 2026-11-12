##The main() function coordinates the modules, while Path makes file paths work on both Windows and macOS.

from pathlib import Path

from data_loader import load_sales
from data_cleaner import clean_sales
from database import insert_sales
from analytics import (
    calculate_kpis,
    revenue_by_product,
    revenue_by_category
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "retail_sales.csv"


def main():
    raw_data = load_sales(DATA_FILE)

    transactions, rejected = clean_sales(raw_data)

    insert_sales(transactions)

    kpis = calculate_kpis(transactions)

    print("\n=== RETAIL INTELLIGENCE PLATFORM ===")

    print("\nBUSINESS KPIs")
    for metric, value in kpis.items():
        print(f"{metric}: {value}")

    print("\nREVENUE BY PRODUCT")
    for product, revenue in revenue_by_product(transactions).items():
        print(f"{product}: ${revenue:,.2f}")

    print("\nREVENUE BY CATEGORY")
    for category, revenue in revenue_by_category(transactions).items():
        print(f"{category}: ${revenue:,.2f}")

    print(f"\nRejected transactions: {len(rejected)}")


if __name__ == "__main__":
    main()
