import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    getEscalationSummary,
    getEscalations,
    resolveEscalation,
} from "../services/api";


const STATUS_STYLES = {
    PENDING: "esc-pending",
    APPROVED: "esc-approved",
    REJECTED: "esc-rejected",
};


function EscalationQueue({ merchantId }) {

    const [escalations, setEscalations] =
        useState([]);

    const [summary, setSummary] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState(null);

    const [resolving, setResolving] =
        useState(null);

    const [notes, setNotes] =
        useState({});


    const load = useCallback(async () => {

        try {

            setLoading(true);
            setError(null);

            const [escData, sumData] =
                await Promise.all([

                    getEscalations(
                        merchantId || null
                    ),

                    getEscalationSummary(
                        merchantId || null
                    ),

                ]);

            setEscalations(
                escData.escalations || []
            );

            setSummary(sumData);

        } catch (err) {

            setError(
                "Failed to load escalations."
            );

        } finally {

            setLoading(false);

        }

    }, [merchantId]);


    useEffect(() => {
        load();
    }, [load]);


    async function handleResolve(
        escalationId,
        status
    ) {

        setResolving(escalationId);

        try {

            await resolveEscalation(
                escalationId,
                status,
                notes[escalationId] || "",
            );

            await load();

        } catch (err) {

            console.error(
                "Failed to resolve:",
                err
            );

        } finally {

            setResolving(null);

        }

    }


    if (loading) {

        return (

            <div className="escalation-loading">

                <div className="loading-spinner" />

                <p>
                    Loading escalation queue...
                </p>

            </div>

        );

    }


    if (error) {

        return (

            <div className="escalation-error">

                <p>{error}</p>

                <button
                    className="retry-button"
                    onClick={load}
                >
                    Retry
                </button>

            </div>

        );

    }


    return (

        <div className="escalation-queue">

            {/* =================================
                SUMMARY CARDS
            ================================= */}

            {summary && (

                <section className="esc-summary">

                    <div className="esc-stat">
                        <span>Total</span>
                        <strong>
                            {summary.total}
                        </strong>
                    </div>

                    <div className="esc-stat esc-stat-pending">
                        <span>Pending</span>
                        <strong>
                            {summary.pending}
                        </strong>
                    </div>

                    <div className="esc-stat esc-stat-approved">
                        <span>Approved</span>
                        <strong>
                            {summary.approved}
                        </strong>
                    </div>

                    <div className="esc-stat esc-stat-rejected">
                        <span>Rejected</span>
                        <strong>
                            {summary.rejected}
                        </strong>
                    </div>

                </section>

            )}


            {/* =================================
                ESCALATION TABLE
            ================================= */}

            <section className="esc-table-section">

                <div className="section-heading">

                    <div>

                        <p className="eyebrow">
                            COMPLIANCE QUEUE
                        </p>

                        <h2>
                            Escalation queue
                        </h2>

                    </div>

                    <button
                        className="filter-button"
                        onClick={load}
                    >
                        Refresh
                    </button>

                </div>


                {escalations.length === 0 ? (

                    <div className="empty-state">
                        No escalations found.
                        Escalations are auto-created
                        when transactions require
                        human review.
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <table>

                            <thead>

                                <tr>

                                    <th>
                                        Escalation ID
                                    </th>

                                    <th>
                                        Transaction
                                    </th>

                                    <th>
                                        Reason
                                    </th>

                                    <th>
                                        Status
                                    </th>

                                    <th>
                                        Created
                                    </th>

                                    <th>
                                        Notes
                                    </th>

                                    <th>
                                        Action
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {escalations.map(
                                    (esc) => (

                                        <tr
                                            key={
                                                esc.escalation_id
                                            }
                                        >

                                            <td>
                                                <code className="run-id">
                                                    {
                                                        esc.escalation_id
                                                    }
                                                </code>
                                            </td>

                                            <td>
                                                <code className="run-id">
                                                    {
                                                        esc.transaction_id
                                                    }
                                                </code>
                                            </td>

                                            <td className="esc-reason">
                                                {
                                                    esc.reason
                                                }
                                            </td>

                                            <td>
                                                <span
                                                    className={
                                                        `esc-badge ${STATUS_STYLES[esc.status] || ""}`
                                                    }
                                                >
                                                    {
                                                        esc.status
                                                    }
                                                </span>
                                            </td>

                                            <td>
                                                {new Date(
                                                    esc.created_at
                                                ).toLocaleString(
                                                    "en-IN"
                                                )}
                                            </td>

                                            <td>

                                                {esc.status ===
                                                "PENDING" ? (

                                                    <input
                                                        className="esc-notes-input"
                                                        placeholder="Add notes..."
                                                        value={
                                                            notes[
                                                                esc.escalation_id
                                                            ] || ""
                                                        }
                                                        onChange={
                                                            (e) =>
                                                                setNotes(
                                                                    (prev) => ({
                                                                        ...prev,
                                                                        [esc.escalation_id]:
                                                                            e.target.value,
                                                                    })
                                                                )
                                                        }
                                                    />

                                                ) : (

                                                    <span className="esc-notes-text">
                                                        {
                                                            esc.notes ||
                                                            "—"
                                                        }
                                                    </span>

                                                )}

                                            </td>

                                            <td>

                                                {esc.status ===
                                                "PENDING" ? (

                                                    <div className="esc-actions">

                                                        <button
                                                            className="esc-approve-btn"
                                                            disabled={
                                                                resolving ===
                                                                esc.escalation_id
                                                            }
                                                            onClick={() =>
                                                                handleResolve(
                                                                    esc.escalation_id,
                                                                    "APPROVED"
                                                                )
                                                            }
                                                        >
                                                            Approve
                                                        </button>

                                                        <button
                                                            className="esc-reject-btn"
                                                            disabled={
                                                                resolving ===
                                                                esc.escalation_id
                                                            }
                                                            onClick={() =>
                                                                handleResolve(
                                                                    esc.escalation_id,
                                                                    "REJECTED"
                                                                )
                                                            }
                                                        >
                                                            Reject
                                                        </button>

                                                    </div>

                                                ) : (

                                                    <span className="esc-resolved-at">
                                                        {esc.resolved_at
                                                            ? new Date(
                                                                esc.resolved_at
                                                            ).toLocaleDateString(
                                                                "en-IN"
                                                            )
                                                            : "—"}
                                                    </span>

                                                )}

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </section>

        </div>

    );

}


export default EscalationQueue;
