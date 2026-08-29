from sqlalchemy import text
from sqlalchemy.orm import Session


def get_merchants(
    db: Session,
):
    """Return merchants available in RecoverOS."""

    query = text(
        """
        SELECT
            merchant_id,
            merchant_name,
            industry,
            monthly_volume
        FROM merchants
        ORDER BY merchant_id
        """
    )

    rows = (
        db.execute(query)
        .mappings()
        .all()
    )

    return [
        {
            "merchant_id": row["merchant_id"],
            "name": row["merchant_name"],
            "industry": row["industry"],
            "monthly_volume": int(
                row["monthly_volume"]
                or 0
            ),
        }
        for row in rows
    ]