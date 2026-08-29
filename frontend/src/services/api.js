const API_BASE_URL = "http://127.0.0.1:8000";


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