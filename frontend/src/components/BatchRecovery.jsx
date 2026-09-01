import {
    useEffect,
    useState,
} from "react";

import {
    getBatchHistory,
    runBatchRecovery,
} from "../services/api";


function BatchRecovery({ merchantId }) {

    const [running, setRunning] =
        useState(false);

    const [result, setResult] =
        useState(null);

    const [history, setHistory] =
        useState([]);

    const [error, setError] =
        useState(null);


    useEffect(() => {

        getBatchHistory(merchantId || null)
            .then(
                (data) =>
                    setHistory(
                        data.runs || []
                    )
            )
            .catch(console.error);

    }, [merchantId]);


    async function handleRun() {

        setRunning(true);
        setError(null);
        setResult(null);

        try {

            const data =
                await runBatchRecovery(
                    merchantId || null
                );

            setResult(data);

            getBatchHistory(
                merchantId || null
            )
                .then(
                    (d) =>
                        setHistory(
                            d.runs || []
                        )
                )
                .catch(console.error);

        } catch (err) {

            setError(
                "Batch recovery failed. Please try again."
            );

        } finally {

            setRunning(false);

        }

    }


    return (

        <section className="batch-section">

            <div className="section-heading">

                <div>

                    <p className="eyebrow">
                        BATCH ENGINE
                    </p>

                    <h2>
                        Batch recovery
                    </h2>

                </div>


                <button
                    className="batch-run-button"
                    onClick={handleRun}
                    disabled={running}
                >
                    {running
                        ? "Running..."
                        : "Run batch recovery"}
                </button>

            </div>


            {result && (

                <div className="batch-result">

                    <div className="batch-stat">
                        <span>Attempted</span>
                        <strong>
                            {result.attempted}
                        </strong>
                    </div>

                    <div className="batch-stat">
                        <span>Executed</span>
                        <strong>
                            {result.executed}
                        </strong>
                    </div>

                    <div className="batch-stat">
                        <span>Blocked</span>
                        <strong>
                            {result.blocked}
                        </strong>
                    </div>

                    <div className="batch-stat">
                        <span>Skipped</span>
                        <strong>
                            {result.skipped}
                        </strong>
                    </div>

                    <div className="batch-stat batch-stat-amount">
                        <span>
                            Potential recovery
                        </span>
                        <strong>
                            ₹
                            {Number(
                                result.potential_amount
                                || 0
                            ).toLocaleString(
                                "en-IN",
                                {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                }
                            )}
                        </strong>
                    </div>

                </div>

            )}


            {error && (

                <p className="batch-error">
                    {error}
                </p>

            )}


            {history.length > 0 && (

                <div className="table-wrapper batch-history-table">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Run ID
                                </th>

                                <th>
                                    Started
                                </th>

                                <th>
                                    Attempted
                                </th>

                                <th>
                                    Executed
                                </th>

                                <th>
                                    Blocked
                                </th>

                                <th>
                                    Potential value
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {history.map(
                                (run) => (

                                    <tr
                                        key={
                                            run.run_id
                                        }
                                    >

                                        <td>
                                            <code className="run-id">
                                                {
                                                    run.run_id
                                                }
                                            </code>
                                        </td>

                                        <td>
                                            {new Date(
                                                run.started_at
                                            ).toLocaleString(
                                                "en-IN"
                                            )}
                                        </td>

                                        <td>
                                            {
                                                run.attempted
                                            }
                                        </td>

                                        <td>
                                            <strong>
                                                {
                                                    run.executed
                                                }
                                            </strong>
                                        </td>

                                        <td>
                                            {
                                                run.blocked
                                            }
                                        </td>

                                        <td>
                                            ₹
                                            {Number(
                                                run.potential_amount
                                                || 0
                                            ).toLocaleString(
                                                "en-IN",
                                                {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2,
                                                }
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

    );

}


export default BatchRecovery;
