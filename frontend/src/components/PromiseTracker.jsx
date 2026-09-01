import {
    useEffect,
    useState,
} from "react";

import {
    getPromises,
    getPromiseSummary,
    updatePromiseStatus,
} from "../services/api";


function PromiseTracker({
    merchantId = null,
}) {

    const [promises, setPromises] =
        useState([]);

    const [summary, setSummary] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState(null);

    const [updating, setUpdating] =
        useState(null);


    async function loadPromises() {

        try {

            setLoading(true);
            setError(null);

            const [
                promiseData,
                summaryData,
            ] = await Promise.all([
                getPromises(merchantId),
                getPromiseSummary(merchantId),
            ]);

            setPromises(
                promiseData.promises || []
            );

            setSummary(summaryData);

        } catch (err) {

            console.error(
                "Promise loading error:",
                err
            );

            setError(
                "Unable to load promise-to-pay data."
            );

        } finally {

            setLoading(false);

        }

    }


    useEffect(() => {

        loadPromises();

    }, [merchantId]);


    async function handleStatus(
        promiseId,
        status
    ) {

        try {

            setUpdating(promiseId);

            await updatePromiseStatus(
                promiseId,
                status
            );

            await loadPromises();

        } catch (err) {

            console.error(
                "Promise update error:",
                err
            );

            setError(
                "Unable to update promise status."
            );

        } finally {

            setUpdating(null);

        }

    }


    function money(value) {

        return Number(
            value || 0
        ).toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        );

    }


    function formatDate(value) {

        if (!value) {
            return "—";
        }

        return new Date(
            value
        ).toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );

    }


    if (loading) {

        return (
            <section className="promise-section">

                <div className="section-heading">
                    <div>
                        <p className="eyebrow">
                            COLLECTION INTELLIGENCE
                        </p>

                        <h2>
                            Promise-to-Pay Tracker
                        </h2>
                    </div>
                </div>

                <div className="empty-state">
                    Loading promises...
                </div>

            </section>
        );

    }


    return (

        <section className="promise-section">

            <div className="section-heading">

                <div>

                    <p className="eyebrow">
                        COLLECTION INTELLIGENCE
                    </p>

                    <h2>
                        Promise-to-Pay Tracker
                    </h2>

                    <p>
                        Track customer payment
                        commitments and identify
                        broken promises requiring
                        follow-up.
                    </p>

                </div>

                <span>
                    {summary?.total_promises || 0}
                    {" "}promises
                </span>

            </div>


            {error && (

                <div className="dashboard-warning">
                    <div>
                        <strong>
                            Promise tracker warning
                        </strong>

                        <span>
                            {error}
                        </span>
                    </div>
                </div>

            )}


            <div className="promise-metrics">

                <div className="analytics-card">
                    <span>
                        Total promises
                    </span>

                    <strong>
                        {summary?.total_promises || 0}
                    </strong>

                    <small>
                        Customer commitments
                    </small>
                </div>


                <div className="analytics-card">
                    <span>
                        Pending
                    </span>

                    <strong>
                        {summary?.pending || 0}
                    </strong>

                    <small>
                        Awaiting payment
                    </small>
                </div>


                <div className="analytics-card">
                    <span>
                        Kept
                    </span>

                    <strong>
                        {summary?.kept || 0}
                    </strong>

                    <small>
                        Successfully honored
                    </small>
                </div>


                <div className="analytics-card">
                    <span>
                        Broken
                    </span>

                    <strong>
                        {summary?.broken || 0}
                    </strong>

                    <small>
                        Requires follow-up
                    </small>
                </div>


                <div className="analytics-card">
                    <span>
                        Promised amount
                    </span>

                    <strong>
                        ₹{money(
                            summary?.promised_amount
                        )}
                    </strong>

                    <small>
                        Value under commitment
                    </small>
                </div>

            </div>


            <div className="table-wrapper">

                <table>

                    <thead>

                        <tr>
                            <th>Promise</th>
                            <th>Customer</th>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Promise date</th>
                            <th>Status</th>
                            <th>Update</th>
                        </tr>

                    </thead>


                    <tbody>

                        {promises.length === 0 ? (

                            <tr>

                                <td
                                    colSpan="7"
                                    className="empty-state"
                                >
                                    No promises found for
                                    this merchant.
                                </td>

                            </tr>

                        ) : (

                            promises.map(
                                (promise) => (

                                    <tr
                                        key={
                                            promise.promise_id
                                        }
                                    >

                                        <td>
                                            <strong>
                                                {
                                                    promise.promise_id
                                                }
                                            </strong>
                                        </td>

                                        <td>
                                            {
                                                promise.customer_id
                                            }
                                        </td>

                                        <td>
                                            {
                                                promise.transaction_id
                                            }
                                        </td>

                                        <td>
                                            ₹{money(
                                                promise.promised_amount
                                            )}
                                        </td>

                                        <td>
                                            {formatDate(
                                                promise.promise_date
                                            )}
                                        </td>

                                        <td>

                                            <span
                                                className={
                                                    `promise-status promise-${String(
                                                        promise.status
                                                    ).toLowerCase()}`
                                                }
                                            >
                                                {
                                                    promise.status
                                                }
                                            </span>

                                        </td>

                                        <td>

                                            <select
                                                value={
                                                    promise.status
                                                }
                                                disabled={
                                                    updating ===
                                                    promise.promise_id
                                                }
                                                onChange={(event) =>
                                                    handleStatus(
                                                        promise.promise_id,
                                                        event.target.value
                                                    )
                                                }
                                            >
                                                <option value="PENDING">
                                                    Pending
                                                </option>

                                                <option value="KEPT">
                                                    Kept
                                                </option>

                                                <option value="BROKEN">
                                                    Broken
                                                </option>

                                                <option value="CANCELLED">
                                                    Cancelled
                                                </option>
                                            </select>

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


export default PromiseTracker;