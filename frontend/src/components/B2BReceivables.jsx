import { useEffect, useState } from "react";
import { getB2BReceivables } from "../services/api";

const STRATEGY_STYLES = {
    account_manager_escalation: "wf-action-high",
    payment_plan_offer: "wf-action-medium",
    priority_retry: "wf-action-low",
};

const STRATEGY_LABELS = {
    account_manager_escalation: "Account Manager",
    payment_plan_offer: "Payment Plan",
    priority_retry: "Priority Retry",
};

function fmt(amount) {
    return Number(amount || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function B2BReceivables({ merchantId }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        getB2BReceivables(merchantId || null)
            .then(setData)
            .catch(() => setError("Failed to load B2B receivables data."))
            .finally(() => setLoading(false));
    }, [merchantId]);

    if (loading) return <div className="wf-loading"><div className="loading-spinner" /><p>Loading B2B receivables data...</p></div>;
    if (error) return <div className="wf-error">{error}</div>;

    const { summary, receivables } = data || {};

    return (
        <div className="wf-section">
            <div className="section-heading">
                <div>
                    <p className="eyebrow">B2B RECEIVABLES</p>
                    <h2>B2B receivables collection</h2>
                    <p className="wf-desc">
                        High-value and enterprise customer failures with tailored collection strategies — account manager, payment plans, or priority retry.
                    </p>
                </div>
            </div>

            {summary && (
                <div className="wf-summary">
                    <div className="wf-stat">
                        <span>Total receivables</span>
                        <strong>{summary.total_receivables}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Total value</span>
                        <strong>₹{fmt(summary.total_receivables_value)}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Account manager</span>
                        <strong>{summary.account_manager_escalation}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Payment plans</span>
                        <strong>{summary.payment_plan_offer}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Priority retry</span>
                        <strong>{summary.priority_retry}</strong>
                    </div>
                </div>
            )}

            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Segment</th>
                            <th>Total outstanding</th>
                            <th>Strategy</th>
                            <th>Instalment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {!receivables?.length ? (
                            <tr><td colSpan="6" className="empty-state">No B2B receivables found.</td></tr>
                        ) : receivables.map(r => (
                            <tr key={r.transaction_id}>
                                <td><code className="run-id">{r.transaction_id}</code></td>
                                <td><strong>₹{fmt(r.amount)}</strong></td>
                                <td><span className="wf-segment">{r.customer_segment}</span></td>
                                <td className="wf-outstanding">₹{fmt(r.total_outstanding)}</td>
                                <td><span className={`wf-action-badge ${STRATEGY_STYLES[r.collection_strategy] || ""}`}>{STRATEGY_LABELS[r.collection_strategy] || r.collection_strategy}</span></td>
                                <td className="wf-muted">
                                    {r.installment_amount
                                        ? `₹${fmt(r.installment_amount)} × 3`
                                        : "—"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default B2BReceivables;
