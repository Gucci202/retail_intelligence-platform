
from pathlib import Path
from database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
schema_path = BASE_DIR / "sql" / "schema.sql"

connection = get_connection()
cursor = connection.cursor()

try:
    sql = schema_path.read_text(encoding="utf-8")

    for statement in sql.split(";"):
        statement = statement.strip()

        if statement:
            cursor.execute(statement)

    cursor.execute("SHOW TABLES")

    print("\nDatabase tables:")
    for table in cursor.fetchall():
        print(table[0])

    print("\nDatabase setup completed!")

finally:
    cursor.close()
    connection.close()
