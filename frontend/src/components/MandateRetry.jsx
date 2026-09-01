import { useEffect, useState } from "react";
import { getMandateRetry } from "../services/api";

const ACTION_STYLES = {
    immediate_retry: "wf-action-low",
    scheduled_retry: "wf-action-medium",
    retry_with_reminder: "wf-action-medium",
    escalate_to_bank: "wf-action-high",
};

const ACTION_LABELS = {
    immediate_retry: "Immediate (T+2h)",
    scheduled_retry: "Scheduled (T+24h)",
    retry_with_reminder: "Reminder (T+48h)",
    escalate_to_bank: "Escalate to Bank",
};

function fmt(amount) {
    return Number(amount || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function MandateRetry({ merchantId }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        getMandateRetry(merchantId || null)
            .then(setData)
            .catch(() => setError("Failed to load mandate retry data."))
            .finally(() => setLoading(false));
    }, [merchantId]);

    if (loading) return <div className="wf-loading"><div className="loading-spinner" /><p>Loading mandate retry data...</p></div>;
    if (error) return <div className="wf-error">{error}</div>;

    const { summary, mandates } = data || {};

    return (
        <div className="wf-section">
            <div className="section-heading">
                <div>
                    <p className="eyebrow">MANDATE RETRY SEQUENCING</p>
                    <h2>UPI mandate retry queue</h2>
                    <p className="wf-desc">
                        Failed UPI mandates with intelligent retry windows based on amount band and attempt history.
                    </p>
                </div>
            </div>

            {summary && (
                <div className="wf-summary">
                    <div className="wf-stat">
                        <span>Failed mandates</span>
                        <strong>{summary.total_failed_mandates}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Mandate value</span>
                        <strong>₹{fmt(summary.total_mandate_value)}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Immediate retry</span>
                        <strong>{summary.immediate_retry}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Scheduled</span>
                        <strong>{summary.scheduled_retry}</strong>
                    </div>
                    <div className="wf-stat">
                        <span>Bank escalation</span>
                        <strong>{summary.escalate_to_bank}</strong>
                    </div>
                </div>
            )}

            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Attempt</th>
                            <th>Failure reason</th>
                            <th>Retry sequence</th>
                            <th>Rationale</th>
                        </tr>
                    </thead>
                    <tbody>
                        {!mandates?.length ? (
                            <tr><td colSpan="6" className="empty-state">No failed UPI mandates found.</td></tr>
                        ) : mandates.map(m => (
                            <tr key={m.transaction_id}>
                                <td><code className="run-id">{m.transaction_id}</code></td>
                                <td>₹{fmt(m.amount)}</td>
                                <td><span className="wf-attempt">#{m.attempt_number}</span></td>
                                <td><span className="wf-reason">{m.failure_reason}</span></td>
                                <td><span className={`wf-action-badge ${ACTION_STYLES[m.retry_action] || ""}`}>{ACTION_LABELS[m.retry_action] || m.retry_action}</span></td>
                                <td className="wf-rationale">{m.rationale}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default MandateRetry;
