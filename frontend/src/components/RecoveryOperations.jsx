import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    getRecoveryOperations,
} from "../services/api";


function RecoveryOperations({
    merchantId = null,
}) {

    const [data, setData] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState(null);


    const loadOperations =
        useCallback(async () => {

            try {

                setLoading(true);
                setError(null);

                const result =
                    await getRecoveryOperations(
                        20,
                        merchantId
                    );

                setData(result);

            } catch (err) {

                console.error(
                    "Recovery operations error:",
                    err
                );

                setError(
                    "Unable to load recovery operations."
                );

            } finally {

                setLoading(false);

            }

        }, [merchantId]);


    useEffect(() => {

        loadOperations();

    }, [loadOperations]);


    if (loading) {

        return (
            <section className="recovery-operations">

                <div className="section-heading">

                    <div>

                        <p className="eyebrow">
                            OPERATIONS
                        </p>

                        <h2>
                            Recovery operations
                        </h2>

                    </div>

                </div>

                <div className="operations-state">
                    <div className="loading-spinner operations-spinner" />
                    <strong>Loading recovery operations</strong>
                    <span>
                        Fetching recent recovery activity
                        and operational totals.
                    </span>
                </div>

            </section>
        );

    }


    if (error) {

        return (
            <section className="recovery-operations">

                <div className="section-heading">

                    <div>

                        <p className="eyebrow">
                            OPERATIONS
                        </p>

                        <h2>
                            Recovery operations
                        </h2>

                    </div>

                </div>

                <div className="operations-state operations-error">
                    <div className="state-symbol">!</div>
                    <strong>Recovery operations unavailable</strong>
                    <span>{error}</span>
                    <button
                        className="retry-button"
                        onClick={loadOperations}
                    >
                        Retry operations
                    </button>
                </div>

            </section>
        );

    }


    const summary =
        data?.summary || {};

    const activities =
        data?.activities || [];


    return (

        <section className="recovery-operations">

            <div className="section-heading">

                <div>

                    <p className="eyebrow">
                        OPERATIONS
                    </p>

                    <h2>
                        Recovery operations
                    </h2>

                </div>


                <button
                    type="button"
                    className="filter-button operations-refresh"
                    onClick={
                        loadOperations
                    }
                    aria-label="Refresh recovery operations"
                >
                    Refresh
                </button>

            </div>


            <section className="analytics-grid">

                <div className="analytics-card">

                    <span>
                        Total actions
                    </span>

                    <strong>
                        {
                            summary
                                .total_actions ??
                            0
                        }
                    </strong>

                </div>


                <div className="analytics-card">

                    <span>
                        Recovered
                    </span>

                    <strong>
                        {
                            summary
                                .successful_actions ??
                            0
                        }
                    </strong>

                </div>


                <div className="analytics-card">

                    <span>
                        Failed
                    </span>

                    <strong>
                        {
                            summary
                                .failed_actions ??
                            0
                        }
                    </strong>

                </div>


                <div className="analytics-card">

                    <span>
                        Simulated executions
                    </span>

                    <strong>
                        {
                            summary
                                .executed_actions ??
                            0
                        }
                    </strong>

                </div>


                <div className="analytics-card">

                    <span>
                        Revenue recovered
                    </span>

                    <strong>
                        ₹
                        {Number(
                            summary
                                .total_recovered ??
                            0
                        ).toLocaleString(
                            "en-IN",
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                            }
                        )}
                    </strong>

                </div>

            </section>


            <div className="table-wrapper">

                <table>

                    <thead>

                        <tr>

                            <th>
                                Transaction
                            </th>

                            <th>
                                Action
                            </th>

                            <th>
                                Status
                            </th>

                            <th>
                                Recovered
                            </th>

                            <th>
                                Source
                            </th>

                            <th>
                                Executed
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {activities.length === 0 ? (

                            <tr>

                                <td
                                    colSpan="6"
                                    className="empty-state"
                                >
                                    <div className="table-empty-content">
                                        <strong>
                                            No recovery activity
                                        </strong>
                                        <span>
                                            No recovery actions are available
                                            for the current merchant.
                                        </span>
                                    </div>
                                </td>

                            </tr>

                        ) : (

                            activities.map(
                                (activity) => (

                                    <tr
                                        key={
                                            activity.recovery_id
                                        }
                                    >

                                        <td>
                                            {
                                                activity
                                                    .transaction_id
                                            }
                                        </td>


                                        <td>
                                            {
                                                activity.action
                                            }
                                        </td>


                                        <td>

                                            <span
                                                className={
                                                    `action ${String(
                                                        activity.status ||
                                                        ""
                                                    ).toLowerCase()}`
                                                }
                                            >
                                                {
                                                    activity.status
                                                }
                                            </span>

                                        </td>


                                        <td>
                                            ₹
                                            {Number(
                                                activity
                                                    .amount_recovered ??
                                                0
                                            ).toLocaleString(
                                                "en-IN",
                                                {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2,
                                                }
                                            )}
                                        </td>


                                        <td>

                                            <span
                                                className={
                                                    `source-badge ${activity.source}`
                                                }
                                            >
                                                {
                                                    activity.source
                                                }
                                            </span>

                                        </td>


                                        <td>
                                            {
                                                activity.executed_at
                                                    ? new Date(
                                                        activity.executed_at
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )
                                                    : "-"
                                            }
                                        </td>

                                    </tr>

                                )
                            )

                        )}

                    </tbody>

                </table>

            </div>

        </section>

    );

}


export default RecoveryOperations;