def build_prediction_explanation(
    features: dict,
    ml_probability: float,
    signals: dict,
):
    positive_factors = []
    negative_factors = []
    neutral_factors = []

    successful_payments = int(
        features.get(
            "successful_payments",
            0,
        )
        or 0
    )

    previous_recoveries = int(
        features.get(
            "previous_recoveries",
            0,
        )
        or 0
    )

    previous_failures = int(
        signals.get(
            "previous_failures",
            0,
        )
        or 0
    )

    attempt_number = int(
        features.get(
            "attempt_number",
            1,
        )
        or 1
    )

    failure_reason = (
        features.get(
            "failure_reason"
        )
        or "unknown"
    )

    payment_method = (
        features.get(
            "payment_method"
        )
        or ""
    )

    preferred_payment_method = (
        features.get(
            "preferred_payment_method"
        )
        or ""
    )

    customer_segment = (
        features.get(
            "customer_segment"
        )
        or "unknown"
    )

    is_recoverable = bool(
        features.get(
            "is_recoverable",
            False,
        )
    )

    requires_review = bool(
        features.get(
            "requires_review",
            False,
        )
    )

    # =========================================
    # PAYMENT HISTORY
    # =========================================

    if successful_payments >= 20:
        positive_factors.append(
            {
                "factor": "Strong payment history",
                "impact": "positive",
                "detail": (
                    f"Customer has completed "
                    f"{successful_payments} successful payments."
                ),
            }
        )

    elif successful_payments >= 5:
        positive_factors.append(
            {
                "factor": "Established payment history",
                "impact": "positive",
                "detail": (
                    f"Customer has "
                    f"{successful_payments} successful payments."
                ),
            }
        )

    else:
        negative_factors.append(
            {
                "factor": "Limited payment history",
                "impact": "negative",
                "detail": (
                    "There is limited successful-payment "
                    "history available for this customer."
                ),
            }
        )

    # =========================================
    # PREVIOUS RECOVERIES
    # =========================================

    if previous_recoveries >= 3:
        positive_factors.append(
            {
                "factor": "Strong recovery history",
                "impact": "positive",
                "detail": (
                    f"The customer has "
                    f"{previous_recoveries} previous recoveries."
                ),
            }
        )

    elif previous_recoveries > 0:
        positive_factors.append(
            {
                "factor": "Previous recovery success",
                "impact": "positive",
                "detail": (
                    f"The customer has previously recovered "
                    f"{previous_recoveries} failed payment(s)."
                ),
            }
        )

    else:
        neutral_factors.append(
            {
                "factor": "No previous recovery history",
                "impact": "neutral",
                "detail": (
                    "No stored previous recovery success "
                    "was found for this customer."
                ),
            }
        )

    # =========================================
    # PREVIOUS FAILURES
    # =========================================

    if previous_failures == 0:
        positive_factors.append(
            {
                "factor": "No earlier payment failures",
                "impact": "positive",
                "detail": (
                    "No previous failed payments were found "
                    "before this transaction."
                ),
            }
        )

    elif previous_failures <= 2:
        neutral_factors.append(
            {
                "factor": "Limited previous failures",
                "impact": "neutral",
                "detail": (
                    f"The customer has "
                    f"{previous_failures} previous failure(s)."
                ),
            }
        )

    else:
        negative_factors.append(
            {
                "factor": "Repeated payment failures",
                "impact": "negative",
                "detail": (
                    f"The customer has "
                    f"{previous_failures} previous failures."
                ),
            }
        )

    # =========================================
    # ATTEMPT NUMBER
    # =========================================

    if attempt_number <= 1:
        positive_factors.append(
            {
                "factor": "Early payment attempt",
                "impact": "positive",
                "detail": (
                    "This failure occurred on an early "
                    "payment attempt."
                ),
            }
        )

    elif attempt_number >= 3:
        negative_factors.append(
            {
                "factor": "Multiple attempts already made",
                "impact": "negative",
                "detail": (
                    f"This transaction is already on "
                    f"attempt {attempt_number}."
                ),
            }
        )

    # =========================================
    # PAYMENT METHOD PREFERENCE
    # =========================================

    if (
        payment_method
        and preferred_payment_method
        and payment_method ==
        preferred_payment_method
    ):
        positive_factors.append(
            {
                "factor": "Preferred payment method",
                "impact": "positive",
                "detail": (
                    "The failed payment used the customer's "
                    "preferred payment method."
                ),
            }
        )

    elif (
        payment_method
        and preferred_payment_method
    ):
        neutral_factors.append(
            {
                "factor": "Alternative payment method",
                "impact": "neutral",
                "detail": (
                    f"The payment used {payment_method}, "
                    f"while the preferred method is "
                    f"{preferred_payment_method}."
                ),
            }
        )

    # =========================================
    # RECOVERABILITY
    # =========================================

    if is_recoverable:
        positive_factors.append(
            {
                "factor": "Marked as recoverable",
                "impact": "positive",
                "detail": (
                    "The transaction is currently marked "
                    "as eligible for recovery."
                ),
            }
        )

    else:
        negative_factors.append(
            {
                "factor": "Not marked as recoverable",
                "impact": "negative",
                "detail": (
                    "The transaction is not currently "
                    "classified as recoverable."
                ),
            }
        )

    # =========================================
    # REVIEW REQUIREMENT
    # =========================================

    if requires_review:
        negative_factors.append(
            {
                "factor": "Manual review required",
                "impact": "negative",
                "detail": (
                    "The transaction has been flagged "
                    "for manual review."
                ),
            }
        )

    # =========================================
    # CUSTOMER SEGMENT
    # =========================================

    if customer_segment == "high_value":
        positive_factors.append(
            {
                "factor": "High-value customer",
                "impact": "positive",
                "detail": (
                    "The customer belongs to the "
                    "high-value segment."
                ),
            }
        )

    # =========================================
    # FAILURE REASON
    # =========================================

    customer_action_failures = {
        "expired_card",
        "invalid_card",
        "authentication_required",
        "insufficient_funds",
    }

    temporary_failures = {
        "network_error",
        "timeout",
        "gateway_unavailable",
        "processing_error",
    }

    if failure_reason in temporary_failures:
        positive_factors.append(
            {
                "factor": "Temporary failure pattern",
                "impact": "positive",
                "detail": (
                    f"The failure reason '{failure_reason}' "
                    "may be temporary and suitable for retry."
                ),
            }
        )

    elif failure_reason in customer_action_failures:
        negative_factors.append(
            {
                "factor": "Customer action required",
                "impact": "negative",
                "detail": (
                    f"The failure reason '{failure_reason}' "
                    "usually requires customer intervention."
                ),
            }
        )

    else:
        neutral_factors.append(
            {
                "factor": "Payment failure reason",
                "impact": "neutral",
                "detail": (
                    f"Current failure reason: "
                    f"{failure_reason}."
                ),
            }
        )

    # =========================================
    # CONFIDENCE BAND
    # =========================================

    if ml_probability >= 0.70:
        confidence_band = "high"

    elif ml_probability >= 0.40:
        confidence_band = "medium"

    else:
        confidence_band = "low"

    # =========================================
    # SUMMARY
    # =========================================

    if (
        len(positive_factors)
        > len(negative_factors)
    ):
        summary = (
            "The prediction is supported mainly by "
            "positive customer and transaction signals."
        )

    elif (
        len(negative_factors)
        > len(positive_factors)
    ):
        summary = (
            "The prediction is limited by several "
            "risk or payment-failure signals."
        )

    else:
        summary = (
            "The prediction contains a mixture of "
            "positive and negative recovery signals."
        )

    return {
        "probability": round(
            ml_probability,
            4,
        ),
        "confidence_band":
            confidence_band,
        "summary":
            summary,
        "positive_factors":
            positive_factors[:4],
        "negative_factors":
            negative_factors[:4],
        "neutral_factors":
            neutral_factors[:3],
    }