const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";


function buildQuery(params = {}) {

    const searchParams =
        new URLSearchParams();

    Object.entries(params).forEach(
        ([key, value]) => {

            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {
                searchParams.set(
                    key,
                    value
                );
            }

        }
    );

    const query =
        searchParams.toString();

    return query
        ? `?${query}`
        : "";
}


// =========================================
// MERCHANTS
// =========================================

export async function getMerchants() {

    const response = await fetch(
        `${API_BASE_URL}/api/merchants`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch merchants"
        );
    }

    return response.json();
}


// =========================================
// DASHBOARD
// =========================================

export async function getDashboardSummary(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/dashboard/summary${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch dashboard summary"
        );
    }

    return response.json();
}


// =========================================
// RECOVERY OPPORTUNITIES
// =========================================

export async function getOpportunities(
    limit = 10,
    merchantId = null
) {

    const query = buildQuery({
        limit,
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/opportunities${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch recovery opportunities"
        );
    }

    return response.json();
}


// =========================================
// TRANSACTION ANALYSIS
// =========================================

export async function getTransactionAnalysis(
    transactionId
) {

    const response = await fetch(
        `${API_BASE_URL}/api/transactions/${transactionId}/analysis`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch transaction analysis"
        );
    }

    return response.json();
}


// =========================================
// ANALYTICS
// =========================================

export async function getAnalyticsOverview(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/analytics/overview${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch analytics overview"
        );
    }

    return response.json();
}


// =========================================
// RECOVERY TRENDS
// =========================================

export async function getRecoveryTrends(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/analytics/trends${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch recovery trends"
        );
    }

    return response.json();
}


// =========================================
// RECOVERY OPERATIONS
// =========================================

export async function getRecoveryOperations(
    limit = 20,
    merchantId = null
) {

    const query = buildQuery({
        limit,
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/recovery-operations${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch recovery operations"
        );
    }

    return response.json();
}


// =========================================
// EXECUTE RECOVERY ACTION
// =========================================

export async function executeRecoveryAction(
    transactionId
) {

    const response = await fetch(
        `${API_BASE_URL}/api/recovery-actions/${transactionId}/execute`,
        {
            method: "POST",
        }
    );

    if (!response.ok) {
        throw new Error(
            "Failed to execute recovery action"
        );
    }

    return response.json();
}


// =========================================
// PROMISE-TO-PAY
// =========================================

export async function getPromises(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/promises${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch promises"
        );
    }

    return response.json();
}


export async function getPromiseSummary(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/promises/summary${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch promise summary"
        );
    }

    return response.json();
}


export async function updatePromiseStatus(
    promiseId,
    status
) {

    const query = buildQuery({
        status,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/promises/${encodeURIComponent(
            promiseId
        )}/status${query}`,
        {
            method: "PATCH",
        }
    );

    if (!response.ok) {
        throw new Error(
            "Failed to update promise status"
        );
    }

    return response.json();
}


// =========================================
// STOPPING RULES
// =========================================

export async function getStoppingRules() {

    const response = await fetch(
        `${API_BASE_URL}/api/dashboard/stopping-rules`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch stopping rules"
        );
    }

    return response.json();
}


// =========================================
// BATCH RECOVERY
// =========================================

export async function runBatchRecovery(
    merchantId = null
) {

    const response = await fetch(
        `${API_BASE_URL}/api/recovery/batch`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                merchant_id: merchantId || null,
            }),
        }
    );

    if (!response.ok) {
        throw new Error(
            "Failed to run batch recovery"
        );
    }

    return response.json();
}


export async function getBatchHistory(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/recovery/batch/history${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch batch history"
        );
    }

    return response.json();
}


// =========================================
// ESCALATIONS
// =========================================

export async function getEscalations(
    merchantId = null,
    status = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
        status,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/escalations${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch escalations"
        );
    }

    return response.json();
}


export async function getEscalationSummary(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/escalations/summary${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch escalation summary"
        );
    }

    return response.json();
}


export async function resolveEscalation(
    escalationId,
    status,
    notes = ""
) {

    const response = await fetch(
        `${API_BASE_URL}/api/escalations/${encodeURIComponent(
            escalationId
        )}/resolve`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                status,
                notes: notes || null,
            }),
        }
    );

    if (!response.ok) {
        throw new Error(
            "Failed to resolve escalation"
        );
    }

    return response.json();
}


// =========================================
// CHECKOUT ABANDONMENT
// =========================================

export async function getCheckoutAbandonment(
    merchantId = null,
    limit = 20
) {

    const query = buildQuery({
        merchant_id: merchantId,
        limit,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/checkout-abandonment${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch checkout abandonment data"
        );
    }

    return response.json();
}


// =========================================
// SUBSCRIPTION RECOVERY
// =========================================

export async function getSubscriptionRecovery(
    merchantId = null,
    limit = 20
) {

    const query = buildQuery({
        merchant_id: merchantId,
        limit,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/subscription-recovery${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch subscription recovery data"
        );
    }

    return response.json();
}


// =========================================
// MANDATE RETRY
// =========================================

export async function getMandateRetry(
    merchantId = null,
    limit = 20
) {

    const query = buildQuery({
        merchant_id: merchantId,
        limit,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/mandate-retry${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch mandate retry data"
        );
    }

    return response.json();
}


// =========================================
// B2B RECEIVABLES
// =========================================

export async function getB2BReceivables(
    merchantId = null,
    limit = 20
) {

    const query = buildQuery({
        merchant_id: merchantId,
        limit,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/b2b-receivables${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch B2B receivables data"
        );
    }

    return response.json();
}


// =========================================
// RECOVERY IMPACT
// =========================================

export async function getRecoveryImpact(
    merchantId = null
) {

    const query = buildQuery({
        merchant_id: merchantId,
    });

    const response = await fetch(
        `${API_BASE_URL}/api/analytics/impact${query}`
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch recovery impact"
        );
    }

    return response.json();
}