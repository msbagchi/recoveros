import { useEffect, useState } from "react";
import { getSubscriptionRecovery } from "../services/api";

const ACTION_STYLES = {
    scheduled_retry: "wf-action-low",
    customer_notification: "wf-action-medium",
    subscription_pause: "wf-action-high",
};

const ACTION_LABELS = {
    scheduled_retry: "Retry in 24h",
    customer_notification: "Notify Customer",
    subscription_pause: "Pause + Escalate",
};

function fmt(amount) {
    return Number(amount || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function SubscriptionRecovery({ merchantId }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        getSubscriptionRecovery(merchantId || null)
            .then(setData)
            .catch(() => setError("Failed to load subscription recovery data."))
            .finally(() => setLoading(false));
    }, [merchantId]);

    if (loading) return <div className="wf-loading"><div className="loading-spinner" /><p>Loading subscription recovery data...</p></div>;
    if (error) return <div className="wf-error">{error}</div>;

    const { summary, candidates } = data || {};

    return (
        <div className="wf-section">
            <div className="section-heading">
                <div>
                    <p className="eyebrow">SUBSCRIPTION RECOVERY</p>
                    <h2>Failed subscription recovery</h2>
                    <p className="wf-desc">
                        Recurring payment failures ranked by failure streak — smart retry scheduling based on customer history.
                    </p>
                </div>
            </div>

            {summary && (
                <div className="wf-summary">
                    <div className="wf-stat">
                        <span>Failed subscriptions</span>
                        <strong>{summary.total_failed_subscriptions}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Value at risk</span>
                        <strong>₹{fmt(summary.total_value_at_risk)}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Recoverable</span>
                        <strong>{summary.recoverable_subscriptions}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Avg failures</span>
                        <strong>{summary.avg_failures_per_customer}x</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Paused</span>
                        <strong>{summary.subscription_pause}</strong>
                    </div>
                </div>
            )}

            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Failures</th>
                            <th>Segment</th>
                            <th>Retry in</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {!candidates?.length ? (
                            <tr><td colSpan="6" className="empty-state">No failed subscriptions found.</td></tr>
                        ) : candidates.map(c => (
                            <tr key={c.transaction_id}>
                                <td><code className="run-id">{c.transaction_id}</code></td>
                                <td>₹{fmt(c.amount)}</td>
                                <td>
                                    <span className={`wf-failure-count ${c.subscription_failures >= 3 ? "wf-failure-critical" : c.subscription_failures === 2 ? "wf-failure-warn" : ""}`}>
                                        {c.subscription_failures}x
                                    </span>
                                </td>
                                <td><span className="wf-segment">{c.customer_segment}</span></td>
                                <td className="wf-muted">
                                    {c.retry_in_hours ? `${c.retry_in_hours}h` : "—"}
                                </td>
                                <td><span className={`wf-action-badge ${ACTION_STYLES[c.recommended_action] || ""}`}>{ACTION_LABELS[c.recommended_action] || c.recommended_action}</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default SubscriptionRecovery;
