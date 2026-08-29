import os
import pandas as pd
from sqlalchemy import text

from backend.app.db.database import engine


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

DATA_DIR = os.path.join(BASE_DIR, "data", "generated")


FILES = {
    "merchants": "merchants.csv",
    "customers": "customers.csv",
    "transactions": "transactions.csv",
    "recovery_actions": "recovery_actions.csv",
}


def seed_table(table_name, filename):
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    print(f"\nLoading {filename}...")

    df = pd.read_csv(filepath)

    print(f"   Rows found: {len(df)}")

    # Convert NaN values to None for PostgreSQL
    df = df.where(pd.notnull(df), None)

    records = df.to_dict(orient="records")

    if not records:
        print(f"   ⚠️ No data found in {filename}")
        return

    with engine.begin() as connection:
        connection.execute(
            text(f"DELETE FROM {table_name}")
        )

        connection.execute(
            text(
                f"""
                INSERT INTO {table_name}
                ({", ".join(df.columns)})
                VALUES
                ({", ".join(":" + col for col in df.columns)})
                """
            ),
            records,
        )

    print(f"   ✅ Inserted {len(records)} rows into {table_name}")


def seed_database():
    print("\n===================================")
    print("       RecoverOS Database Seed")
    print("===================================")

    for table_name, filename in FILES.items():
        seed_table(table_name, filename)

    print("\n===================================")
    print("   Database seeding completed!")
    print("===================================\n")


if __name__ == "__main__":
    seed_database()