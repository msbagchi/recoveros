from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.promise import PromiseToPay


router = APIRouter(
    prefix="/api/promises",
    tags=["Promise To Pay"],
)


class PromiseCreate(BaseModel):
    promise_id: str
    merchant_id: str
    customer_id: str
    transaction_id: str
    promised_amount: float
    promise_date: datetime
    status: str = "PENDING"


@router.get("")
def get_promises(
    merchant_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(PromiseToPay)

    if merchant_id:
        query = query.filter(
            PromiseToPay.merchant_id == merchant_id
        )

    if status:
        query = query.filter(
            PromiseToPay.status == status.upper()
        )

    promises = (
        query
        .order_by(PromiseToPay.promise_date.asc())
        .all()
    )

    return {
        "count": len(promises),
        "promises": [
            {
                "promise_id": item.promise_id,
                "merchant_id": item.merchant_id,
                "customer_id": item.customer_id,
                "transaction_id": item.transaction_id,
                "promised_amount": item.promised_amount,
                "promise_date": item.promise_date,
                "status": item.status,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in promises
        ],
    }


@router.get("/summary")
def get_promise_summary(
    merchant_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(PromiseToPay)

    if merchant_id:
        query = query.filter(
            PromiseToPay.merchant_id == merchant_id
        )

    promises = query.all()

    pending = sum(
        1 for item in promises
        if item.status == "PENDING"
    )

    kept = sum(
        1 for item in promises
        if item.status == "KEPT"
    )

    broken = sum(
        1 for item in promises
        if item.status == "BROKEN"
    )

    cancelled = sum(
        1 for item in promises
        if item.status == "CANCELLED"
    )

    promised_amount = sum(
        item.promised_amount
        for item in promises
    )

    return {
        "total_promises": len(promises),
        "pending": pending,
        "kept": kept,
        "broken": broken,
        "cancelled": cancelled,
        "promised_amount": round(promised_amount, 2),
    }


@router.post("")
def create_promise(
    payload: PromiseCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(PromiseToPay)
        .filter(
            PromiseToPay.promise_id
            == payload.promise_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Promise ID already exists",
        )

    promise = PromiseToPay(
        promise_id=payload.promise_id,
        merchant_id=payload.merchant_id,
        customer_id=payload.customer_id,
        transaction_id=payload.transaction_id,
        promised_amount=payload.promised_amount,
        promise_date=payload.promise_date,
        status=payload.status.upper(),
    )

    db.add(promise)
    db.commit()
    db.refresh(promise)

    return {
        "success": True,
        "promise_id": promise.promise_id,
        "status": promise.status,
    }


@router.patch("/{promise_id}/status")
def update_promise_status(
    promise_id: str,
    status: str,
    db: Session = Depends(get_db),
):
    allowed_statuses = {
        "PENDING",
        "KEPT",
        "BROKEN",
        "CANCELLED",
    }

    new_status = status.upper()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid promise status",
        )

    promise = (
        db.query(PromiseToPay)
        .filter(
            PromiseToPay.promise_id == promise_id
        )
        .first()
    )

    if not promise:
        raise HTTPException(
            status_code=404,
            detail="Promise not found",
        )

    promise.status = new_status
    promise.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(promise)

    return {
        "success": True,
        "promise_id": promise.promise_id,
        "status": promise.status,
    }