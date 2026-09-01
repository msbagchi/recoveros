import { useEffect, useState } from "react";
import { getCheckoutAbandonment } from "../services/api";

const ACTION_STYLES = {
    send_payment_link: "wf-action-high",
    send_recovery_nudge: "wf-action-medium",
    auto_retry: "wf-action-low",
};

const ACTION_LABELS = {
    send_payment_link: "Payment Link",
    send_recovery_nudge: "Recovery Nudge",
    auto_retry: "Auto Retry",
};

const URGENCY_STYLES = {
    HIGH: "priority-high",
    MEDIUM: "priority-medium",
    LOW: "priority-low",
};

function fmt(amount) {
    return Number(amount || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function CheckoutAbandonment({ merchantId }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        getCheckoutAbandonment(merchantId || null)
            .then(setData)
            .catch(() => setError("Failed to load checkout abandonment data."))
            .finally(() => setLoading(false));
    }, [merchantId]);

    if (loading) return <div className="wf-loading"><div className="loading-spinner" /><p>Loading checkout abandonment data...</p></div>;
    if (error) return <div className="wf-error">{error}</div>;

    const { summary, candidates } = data || {};

    return (
        <div className="wf-section">
            <div className="section-heading">
                <div>
                    <p className="eyebrow">CHECKOUT ABANDONMENT</p>
                    <h2>Abandoned checkout recovery</h2>
                    <p className="wf-desc">
                        Failed one-time payments with temporary errors — customers who dropped mid-checkout.
                    </p>
                </div>
            </div>

            {summary && (
                <div className="wf-summary">
                    <div className="wf-stat">
                        <span>Abandoned</span>
                        <strong>{summary.total_abandoned}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Value at risk</span>
                        <strong>₹{fmt(summary.total_value_at_risk)}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Payment links</span>
                        <strong>{summary.send_payment_link}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Recovery nudges</span>
                        <strong>{summary.send_recovery_nudge}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Auto retry</span>
                        <strong>{summary.auto_retry}</strong>
                    </div>
                </div>
            )}

            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Failure reason</th>
                            <th>Segment</th>
                            <th>Urgency</th>
                            <th>Recommended action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {!candidates?.length ? (
                            <tr><td colSpan="6" className="empty-state">No abandoned checkouts found.</td></tr>
                        ) : candidates.map(c => (
                            <tr key={c.transaction_id}>
                                <td><code className="run-id">{c.transaction_id}</code></td>
                                <td>₹{fmt(c.amount)}</td>
                                <td><span className="wf-reason">{c.failure_reason}</span></td>
                                <td><span className="wf-segment">{c.customer_segment}</span></td>
                                <td><span className={`priority-badge ${URGENCY_STYLES[c.urgency] || ""}`}>{c.urgency}</span></td>
                                <td><span className={`wf-action-badge ${ACTION_STYLES[c.recommended_action] || ""}`}>{ACTION_LABELS[c.recommended_action] || c.recommended_action}</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default CheckoutAbandonment;
