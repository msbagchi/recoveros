from sqlalchemy import text
from sqlalchemy.orm import Session


def get_recovery_operations(
    db: Session,
    limit: int = 20,
    merchant_id: str | None = None,
):
    """
    Return recovery-operation statistics and
    recent recovery activity.
    """

    params = {
        "limit": limit,
    }

    if merchant_id:
        params["merchant_id"] = merchant_id

    # =========================================
    # SUMMARY
    # =========================================

    if merchant_id:

        summary_query = text(
            """
            SELECT
                COUNT(*) AS total_actions,

                COUNT(*) FILTER (
                    WHERE ra.status = 'recovered'
                ) AS successful_actions,

                COUNT(*) FILTER (
                    WHERE ra.status = 'failed'
                ) AS failed_actions,

                COUNT(*) FILTER (
                    WHERE ra.status = 'executed'
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
                ) AS total_recovered

            FROM recovery_actions ra

            JOIN transactions t
                ON ra.transaction_id =
                   t.transaction_id

            WHERE t.merchant_id = :merchant_id
            """
        )

    else:

        summary_query = text(
            """
            SELECT
                COUNT(*) AS total_actions,

                COUNT(*) FILTER (
                    WHERE status = 'recovered'
                ) AS successful_actions,

                COUNT(*) FILTER (
                    WHERE status = 'failed'
                ) AS failed_actions,

                COUNT(*) FILTER (
                    WHERE status = 'executed'
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
                ) AS total_recovered

            FROM recovery_actions
            """
        )

    summary_row = (
        db.execute(
            summary_query,
            params,
        )
        .mappings()
        .first()
    )

    # =========================================
    # RECENT ACTIVITY
    # =========================================

    if merchant_id:

        activity_query = text(
            """
            SELECT
                ra.recovery_id,
                ra.transaction_id,
                ra.action,
                ra.status,
                ra.amount_recovered,
                ra.executed_at,
                t.merchant_id

            FROM recovery_actions ra

            JOIN transactions t
                ON ra.transaction_id =
                   t.transaction_id

            WHERE t.merchant_id = :merchant_id

            ORDER BY
                ra.executed_at DESC,
                ra.id DESC

            LIMIT :limit
            """
        )

    else:

        activity_query = text(
            """
            SELECT
                ra.recovery_id,
                ra.transaction_id,
                ra.action,
                ra.status,
                ra.amount_recovered,
                ra.executed_at,
                t.merchant_id

            FROM recovery_actions ra

            JOIN transactions t
                ON ra.transaction_id =
                   t.transaction_id

            ORDER BY
                ra.executed_at DESC,
                ra.id DESC

            LIMIT :limit
            """
        )

    activity_rows = (
        db.execute(
            activity_query,
            params,
        )
        .mappings()
        .all()
    )

    # =========================================
    # ACTIVITY RESPONSE
    # =========================================

    activities = []

    for row in activity_rows:

        recovery_id = row[
            "recovery_id"
        ]

        is_simulation = (
            recovery_id is not None
            and recovery_id.startswith(
                "SIM-"
            )
        )

        activities.append(
            {
                "recovery_id":
                    recovery_id,

                "transaction_id":
                    row[
                        "transaction_id"
                    ],

                "merchant_id":
                    row[
                        "merchant_id"
                    ],

                "action":
                    row[
                        "action"
                    ],

                "status":
                    row[
                        "status"
                    ],

                "amount_recovered":
                    round(
                        float(
                            row[
                                "amount_recovered"
                            ]
                            or 0
                        ),
                        2,
                    ),

                "executed_at":
                    (
                        row[
                            "executed_at"
                        ].isoformat()
                        if row[
                            "executed_at"
                        ]
                        else None
                    ),

                "source":
                    (
                        "simulation"
                        if is_simulation
                        else "historical"
                    ),
            }
        )

    return {
        "merchant_id":
            merchant_id,

        "summary": {

            "total_actions":
                int(
                    summary_row[
                        "total_actions"
                    ]
                    or 0
                ),

            "successful_actions":
                int(
                    summary_row[
                        "successful_actions"
                    ]
                    or 0
                ),

            "failed_actions":
                int(
                    summary_row[
                        "failed_actions"
                    ]
                    or 0
                ),

            "executed_actions":
                int(
                    summary_row[
                        "executed_actions"
                    ]
                    or 0
                ),

            "total_recovered":
                round(
                    float(
                        summary_row[
                            "total_recovered"
                        ]
                        or 0
                    ),
                    2,
                ),
        },

        "activities":
            activities,
    }