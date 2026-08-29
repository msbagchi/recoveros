from sqlalchemy import text
from sqlalchemy.orm import Session


def get_recovery_trends(
    db: Session,
    merchant_id: str | None = None,
):
    params = {}

    if merchant_id:
        params["merchant_id"] = merchant_id

        query = text(
            """
            SELECT
                DATE(ra.executed_at) AS date,

                COUNT(*) AS total_actions,

                COUNT(
                    CASE
                        WHEN ra.status = 'recovered'
                        THEN 1
                    END
                ) AS successful_recoveries,

                COUNT(
                    CASE
                        WHEN ra.status = 'failed'
                        THEN 1
                    END
                ) AS failed_recoveries,

                COUNT(
                    CASE
                        WHEN ra.status = 'executed'
                        THEN 1
                    END
                ) AS executed_actions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN ra.status = 'recovered'
                            THEN ra.amount_recovered
                            ELSE 0
                        END
                    ),
                    0
                ) AS recovered_amount

            FROM recovery_actions ra

            JOIN transactions t
                ON ra.transaction_id =
                   t.transaction_id

            WHERE t.merchant_id = :merchant_id

            GROUP BY DATE(ra.executed_at)

            ORDER BY DATE(ra.executed_at)
            """
        )

    else:
        query = text(
            """
            SELECT
                DATE(executed_at) AS date,

                COUNT(*) AS total_actions,

                COUNT(
                    CASE
                        WHEN status = 'recovered'
                        THEN 1
                    END
                ) AS successful_recoveries,

                COUNT(
                    CASE
                        WHEN status = 'failed'
                        THEN 1
                    END
                ) AS failed_recoveries,

                COUNT(
                    CASE
                        WHEN status = 'executed'
                        THEN 1
                    END
                ) AS executed_actions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'recovered'
                            THEN amount_recovered
                            ELSE 0
                        END
                    ),
                    0
                ) AS recovered_amount

            FROM recovery_actions

            GROUP BY DATE(executed_at)

            ORDER BY DATE(executed_at)
            """
        )

    rows = (
        db.execute(
            query,
            params,
        )
        .mappings()
        .all()
    )

    trends = []

    for row in rows:

        successful_recoveries = int(
            row["successful_recoveries"]
            or 0
        )

        failed_recoveries = int(
            row["failed_recoveries"]
            or 0
        )

        executed_actions = int(
            row["executed_actions"]
            or 0
        )

        total_actions = int(
            row["total_actions"]
            or 0
        )

        # Only completed historical outcomes are
        # used for the success-rate calculation.
        completed_outcomes = (
            successful_recoveries
            + failed_recoveries
        )

        if completed_outcomes > 0:

            recovery_rate = (
                successful_recoveries
                / completed_outcomes
            ) * 100

        else:

            recovery_rate = 0.0

        trends.append(
            {
                "date": str(
                    row["date"]
                ),

                "total_actions":
                    total_actions,

                "successful_recoveries":
                    successful_recoveries,

                "failed_recoveries":
                    failed_recoveries,

                "executed_actions":
                    executed_actions,

                "recovered_amount":
                    round(
                        float(
                            row[
                                "recovered_amount"
                            ]
                            or 0
                        ),
                        2,
                    ),

                "recovery_rate":
                    round(
                        recovery_rate,
                        2,
                    ),
            }
        )

    return trends