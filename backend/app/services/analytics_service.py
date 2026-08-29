from sqlalchemy import text
from sqlalchemy.orm import Session


def get_analytics_overview(
    db: Session,
    merchant_id: str | None = None,
):
    params = {}

    if merchant_id:
        params["merchant_id"] = merchant_id

    # =========================================
    # TRANSACTION STATISTICS
    # =========================================

    if merchant_id:
        transaction_query = text(
            """
            SELECT
                COUNT(*) AS total_transactions,

                COALESCE(
                    SUM(amount),
                    0
                ) AS total_transaction_value,

                COUNT(
                    CASE
                        WHEN status = 'failed'
                        THEN 1
                    END
                ) AS failed_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'failed'
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS failed_transaction_value,

                COUNT(
                    CASE
                        WHEN is_recoverable = TRUE
                        THEN 1
                    END
                ) AS recoverable_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN is_recoverable = TRUE
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS recoverable_value

            FROM transactions

            WHERE merchant_id = :merchant_id
            """
        )

    else:
        transaction_query = text(
            """
            SELECT
                COUNT(*) AS total_transactions,

                COALESCE(
                    SUM(amount),
                    0
                ) AS total_transaction_value,

                COUNT(
                    CASE
                        WHEN status = 'failed'
                        THEN 1
                    END
                ) AS failed_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'failed'
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS failed_transaction_value,

                COUNT(
                    CASE
                        WHEN is_recoverable = TRUE
                        THEN 1
                    END
                ) AS recoverable_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN is_recoverable = TRUE
                            THEN amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS recoverable_value

            FROM transactions
            """
        )

    transaction_stats = (
        db.execute(
            transaction_query,
            params,
        )
        .mappings()
        .first()
    )

    # =========================================
    # RECOVERY STATISTICS
    # =========================================

    if merchant_id:
        recovery_query = text(
            """
            SELECT
                COUNT(*) AS recovery_actions,

                COALESCE(
                    SUM(
                        ra.amount_recovered
                    ),
                    0
                ) AS recovered_amount,

                COUNT(
                    CASE
                        WHEN ra.status = 'recovered'
                        THEN 1
                    END
                ) AS successful_recoveries

            FROM recovery_actions ra

            JOIN transactions t
                ON ra.transaction_id =
                   t.transaction_id

            WHERE t.merchant_id = :merchant_id
            """
        )

    else:
        recovery_query = text(
            """
            SELECT
                COUNT(*) AS recovery_actions,

                COALESCE(
                    SUM(amount_recovered),
                    0
                ) AS recovered_amount,

                COUNT(
                    CASE
                        WHEN status = 'recovered'
                        THEN 1
                    END
                ) AS successful_recoveries

            FROM recovery_actions
            """
        )

    recovery_stats = (
        db.execute(
            recovery_query,
            params,
        )
        .mappings()
        .first()
    )

    # =========================================
    # VALUES
    # =========================================

    total_transaction_value = float(
        transaction_stats[
            "total_transaction_value"
        ]
        or 0
    )

    failed_transaction_value = float(
        transaction_stats[
            "failed_transaction_value"
        ]
        or 0
    )

    recoverable_value = float(
        transaction_stats[
            "recoverable_value"
        ]
        or 0
    )

    recovered_amount = float(
        recovery_stats[
            "recovered_amount"
        ]
        or 0
    )

    # =========================================
    # RECOVERY RATE
    # =========================================

    if failed_transaction_value > 0:
        recovery_rate = (
            recovered_amount
            / failed_transaction_value
        ) * 100

    else:
        recovery_rate = 0.0

    # =========================================
    # RESPONSE
    # =========================================

    return {
        "merchant_id":
            merchant_id,

        "total_transactions":
            int(
                transaction_stats[
                    "total_transactions"
                ]
                or 0
            ),

        "total_transaction_value":
            round(
                total_transaction_value,
                2,
            ),

        "failed_transactions":
            int(
                transaction_stats[
                    "failed_transactions"
                ]
                or 0
            ),

        "failed_transaction_value":
            round(
                failed_transaction_value,
                2,
            ),

        "recoverable_transactions":
            int(
                transaction_stats[
                    "recoverable_transactions"
                ]
                or 0
            ),

        "recoverable_value":
            round(
                recoverable_value,
                2,
            ),

        "recovery_actions":
            int(
                recovery_stats[
                    "recovery_actions"
                ]
                or 0
            ),

        "successful_recoveries":
            int(
                recovery_stats[
                    "successful_recoveries"
                ]
                or 0
            ),

        "recovered_amount":
            round(
                recovered_amount,
                2,
            ),

        "recovery_rate":
            round(
                recovery_rate,
                2,
            ),
    }