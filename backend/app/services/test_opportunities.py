from backend.app.db.database import SessionLocal

from backend.app.services.opportunity_service import (
    get_recovery_opportunities,
)


db = SessionLocal()

try:

    opportunities = (
        get_recovery_opportunities(
            db,
            limit=10,
        )
    )

    print()
    print(
        "=================================================="
    )
    print(
        "          RECOVEROS OPPORTUNITIES"
    )
    print(
        "=================================================="
    )

    if not opportunities:

        print("No recovery opportunities found.")

    else:

        for index, opportunity in enumerate(
            opportunities,
            start=1,
        ):

            print()
            print(
                f"#{index} "
                f"{opportunity['transaction_id']}"
            )

            print(
                f"   Customer:       "
                f"{opportunity['customer_id']}"
            )

            print(
                f"   Amount:         "
                f"Rs {opportunity['amount']:,.2f}"
            )

            print(
                f"   Failure:        "
                f"{opportunity['failure_reason']}"
            )

            print(
                f"   Recovery chance:"
                f" {opportunity['ml_probability'] * 100:.1f}%"
            )

            print(
                f"   Expected value: "
                f"Rs {opportunity['expected_recovery']:,.2f}"
            )

            print(
                f"   Recommendation: "
                f"{opportunity['recommended_action']}"
            )

    print()
    print(
        "=================================================="
    )

finally:

    db.close()