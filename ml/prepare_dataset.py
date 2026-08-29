import os

import pandas as pd
from sqlalchemy import create_engine, text

from backend.app.config import settings


OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__),
    "data",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_training_data():
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    query = text(
        """
        SELECT
            t.transaction_id,
            t.amount,
            t.currency,
            t.payment_method,
            t.transaction_type,
            t.failure_reason,
            t.attempt_number,
            t.is_recoverable,
            t.requires_review,

            c.segment AS customer_segment,
            c.successful_payments,
            c.lifetime_value,
            c.previous_recoveries,
            c.preferred_payment_method,

            CASE
                WHEN r.status = 'recovered'
                THEN 1
                ELSE 0
            END AS recovered

        FROM recovery_actions r

        JOIN transactions t
            ON t.transaction_id = r.transaction_id

        JOIN customers c
            ON c.customer_id = t.customer_id

        WHERE r.status IN ('recovered', 'failed')
        """
    )

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


def main():
    print()
    print("======================================")
    print("      RECOVEROS ML DATASET")
    print("======================================")

    df = load_training_data()

    print(f"Rows loaded: {len(df)}")
    print()

    print("Target distribution:")
    print(df["recovered"].value_counts())

    print()
    print("Recovery rate:")
    print(
        f"{df['recovered'].mean() * 100:.2f}%"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        "recovery_training_data.csv",
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print()
    print(f"Dataset saved to:")
    print(output_path)

    print()
    print("Features:")

    for column in df.columns:
        print(f"  - {column}")

    print()
    print("======================================")
    print("        DATASET READY")
    print("======================================")


if __name__ == "__main__":
    main()