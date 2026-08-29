import { useEffect, useState } from "react";

import {
    executeRecoveryAction,
    getTransactionAnalysis,
} from "../services/api";


function TransactionPanel({
    transactionId,
    onClose,
}) {

    const [analysis, setAnalysis] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState(null);

    const [executing, setExecuting] =
        useState(false);

    const [executionResult, setExecutionResult] =
        useState(null);


    async function loadAnalysis() {

        try {

            setLoading(true);
            setError(null);

            const data =
                await getTransactionAnalysis(
                    transactionId
                );

            setAnalysis(data);

        } catch (err) {

            console.error(err);

            setError(
                "Unable to load transaction analysis."
            );

        } finally {

            setLoading(false);

        }

    }


    useEffect(() => {

        loadAnalysis();

    }, [transactionId]);


    async function handleExecuteRecovery() {

        try {

            setExecuting(true);

            setExecutionResult(null);

            const result =
                await executeRecoveryAction(
                    transactionId
                );

            setExecutionResult(
                result
            );

            if (
                result.status === "executed"
            ) {

                await loadAnalysis();

            }

        } catch (err) {

            console.error(err);

            setExecutionResult({
                success: false,
                status: "error",
                message:
                    "Recovery execution failed.",
            });

        } finally {

            setExecuting(false);

        }

    }


    if (loading) {

        return (
            <div className="panel-overlay">

                <div className="transaction-panel">

                    <button
                        className="close-button"
                        onClick={onClose}
                    >
                        ×
                    </button>

                    <div className="panel-state">
                        <div className="loading-spinner panel-spinner" />
                        <p className="eyebrow">TRANSACTION INTELLIGENCE</p>
                        <h3>Analysing transaction</h3>
                        <p>
                            Loading payment signals, recovery
                            history and decision intelligence.
                        </p>
                    </div>

                </div>

            </div>
        );
    }


    if (error || !analysis) {

        return (
            <div className="panel-overlay">

                <div className="transaction-panel">

                    <button
                        className="close-button"
                        onClick={onClose}
                    >
                        ×
                    </button>

                    <div className="panel-state error-panel-state">
                        <div className="state-symbol">!</div>
                        <p className="eyebrow">ANALYSIS ERROR</p>
                        <h3>Transaction analysis unavailable</h3>
                        <p>
                            {error ||
                                "Unable to load transaction analysis."}
                        </p>
                        <button
                            className="retry-button"
                            onClick={loadAnalysis}
                        >
                            Retry analysis
                        </button>
                    </div>

                </div>

            </div>
        );
    }


    const transaction =
        analysis.transaction;

    const decision =
        analysis.decision;

    const history =
        analysis.recovery_history || [];

    const explanation =
        analysis.explanation || {};

    const positiveFactors =
        explanation.positive_factors || [];

    const negativeFactors =
        explanation.negative_factors || [];

    const neutralFactors =
        explanation.neutral_factors || [];

    const mlProbability =
        Number(
            analysis.ml_probability || 0
        ) * 100;


    const canExecute =
        decision.action === "RETRY"
        || decision.action === "REMIND";


    return (

        <div
            className="panel-overlay"
            onClick={onClose}
        >

            <div
                className="transaction-panel"
                onClick={(event) =>
                    event.stopPropagation()
                }
            >

                <button
                    className="close-button"
                    onClick={onClose}
                >
                    ×
                </button>


                <p className="eyebrow">
                    TRANSACTION INTELLIGENCE
                </p>

                <h2>
                    {transaction.transaction_id}
                </h2>


                {/* =================================
                    TRANSACTION META
                ================================= */}

                <div className="transaction-meta">

                    <div>

                        <span>
                            Amount
                        </span>

                        <strong>
                            ₹
                            {Number(
                                transaction.amount
                            ).toLocaleString(
                                "en-IN",
                                {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                }
                            )}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Failure
                        </span>

                        <strong>
                            {
                                transaction.failure_reason
                            }
                        </strong>

                    </div>


                    <div>

                        <span>
                            Previous failures
                        </span>

                        <strong>
                            {
                                transaction.previous_failures
                            }
                        </strong>

                    </div>

                </div>


                {/* =================================
                    ML SIGNAL
                ================================= */}

                <div className="ml-section">

                    <div className="section-heading">

                        <div>

                            <p className="eyebrow">
                                ML SIGNAL
                            </p>

                            <h3>
                                Recovery probability
                            </h3>

                        </div>


                        <strong className="probability">

                            {mlProbability.toFixed(1)}%

                        </strong>

                    </div>


                    <div className="probability-track">

                        <div
                            className="probability-fill"
                            style={{
                                width:
                                    `${Math.min(
                                        mlProbability,
                                        100
                                    )}%`,
                            }}
                        />

                    </div>

                </div>


                {/* =================================
                    EXPLAINABILITY
                ================================= */}

                <div className="explainability-section">

                    <div className="section-heading">

                        <div>

                            <p className="eyebrow">
                                AI EXPLAINABILITY
                            </p>

                            <h3>
                                Why this prediction?
                            </h3>

                        </div>


                        <span
                            className={
                                `confidence-band ${
                                    explanation.confidence_band
                                    || "medium"
                                }`
                            }
                        >
                            {
                                (
                                    explanation.confidence_band
                                    || "medium"
                                ).toUpperCase()
                            }
                        </span>

                    </div>


                    <p className="explanation-summary">
                        {
                            explanation.summary
                            || "Prediction explanation is unavailable."
                        }
                    </p>


                    <div className="factor-groups">

                        {positiveFactors.length > 0 && (

                            <div className="factor-group positive">

                                <div className="factor-group-title">

                                    <span className="factor-symbol">
                                        +
                                    </span>

                                    <strong>
                                        Positive signals
                                    </strong>

                                </div>


                                {positiveFactors.map(
                                    (item, index) => (

                                        <div
                                            className="factor-card"
                                            key={
                                                `positive-${index}`
                                            }
                                        >

                                            <strong>
                                                {item.factor}
                                            </strong>

                                            <p>
                                                {item.detail}
                                            </p>

                                        </div>

                                    )
                                )}

                            </div>

                        )}


                        {negativeFactors.length > 0 && (

                            <div className="factor-group negative">

                                <div className="factor-group-title">

                                    <span className="factor-symbol">
                                        −
                                    </span>

                                    <strong>
                                        Risk signals
                                    </strong>

                                </div>


                                {negativeFactors.map(
                                    (item, index) => (

                                        <div
                                            className="factor-card"
                                            key={
                                                `negative-${index}`
                                            }
                                        >

                                            <strong>
                                                {item.factor}
                                            </strong>

                                            <p>
                                                {item.detail}
                                            </p>

                                        </div>

                                    )
                                )}

                            </div>

                        )}


                        {neutralFactors.length > 0 && (

                            <div className="factor-group neutral">

                                <div className="factor-group-title">

                                    <span className="factor-symbol">
                                        •
                                    </span>

                                    <strong>
                                        Context signals
                                    </strong>

                                </div>


                                {neutralFactors.map(
                                    (item, index) => (

                                        <div
                                            className="factor-card"
                                            key={
                                                `neutral-${index}`
                                            }
                                        >

                                            <strong>
                                                {item.factor}
                                            </strong>

                                            <p>
                                                {item.detail}
                                            </p>

                                        </div>

                                    )
                                )}

                            </div>

                        )}

                    </div>


                    <div className="explainability-footer">

                        <span>
                            ML probability
                        </span>

                        <strong>
                            {mlProbability.toFixed(1)}%
                        </strong>

                        <span>
                            •
                        </span>

                        <span>
                            Confidence
                        </span>

                        <strong>
                            {
                                (
                                    explanation.confidence_band
                                    || "medium"
                                ).toUpperCase()
                            }
                        </strong>

                    </div>

                </div>


                {/* =================================
                    DECISION
                ================================= */}

                <div className="decision-box">

                    <p className="eyebrow">
                        RECOVERY DECISION
                    </p>


                    <div
                        className={
                            `decision-action decision-${String(
                                decision.action || "review"
                            ).toLowerCase()}`
                        }
                    >
                        {decision.action}
                    </div>


                    <div className="decision-stats">

                        <div>

                            <span>
                                Confidence
                            </span>

                            <strong>
                                {(
                                    Number(
                                        decision.confidence
                                    ) * 100
                                ).toFixed(0)}
                                %
                            </strong>

                        </div>


                        <div>

                            <span>
                                Expected recovery
                            </span>

                            <strong>

                                ₹
                                {Number(
                                    decision.expected_recovery
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


                    <div className="reason">

                        <span>
                            Why RecoverOS recommends this
                        </span>

                        <p>
                            {decision.reason}
                        </p>

                    </div>


                    {/* =================================
                        EXECUTION
                    ================================= */}

                    <div className="execution-section">

                        <button
                            className={
                                canExecute
                                    ? "execute-button"
                                    : "execute-button blocked"
                            }
                            onClick={
                                handleExecuteRecovery
                            }
                            disabled={
                                executing || !canExecute
                            }
                        >

                            {executing
                                ? "Executing..."
                                : getActionButtonLabel(
                                    decision.action
                                )}

                        </button> 


{!canExecute && (

    <p className="guardrail-note">

        {decision.action === "ESCALATE"
            ? "Automatic execution is blocked. This transaction requires manual operator review."
            : decision.action === "CUSTOMER_ACTION"
                ? "Automatic execution is blocked. The customer must resolve the payment issue first."
                : "Automatic execution is unavailable for this action."}

    </p>

)}


                        {executionResult && (

                            <div
                                className={
                                    executionResult.success
                                        ? "execution-result success"
                                        : "execution-result blocked-result"
                                }
                            >

                                <strong>

                                    {executionResult.status === "executed"
                                        ? "Recovery action executed"
                                        : executionResult.status === "blocked"
                                            ? "Execution blocked"
                                            : "Execution result"}

                                </strong>


                                <p>
                                    {
                                        executionResult.message
                                    }
                                </p>


                                {executionResult.recovery_id && (

                                    <small>

                                        Recovery ID:{" "}
                                        {
                                            executionResult.recovery_id
                                        }

                                    </small>

                                )}

                            </div>

                        )}

                    </div>

                </div>


                {/* =================================
                    AUDIT TRAIL
                ================================= */}

                <div className="timeline-section">

                    <div className="section-heading">

                        <div>

                            <p className="eyebrow">
                                AUDIT TRAIL
                            </p>

                            <h3>
                                Recovery history
                            </h3>

                        </div>


                        <span className="history-count">
                            {history.length}
                        </span>

                    </div>


                    {history.length === 0 ? (

                        <div className="empty-history">

                            <strong>
                                No recovery actions yet
                            </strong>

                            <p>
                                Recovery activity for this
                                transaction will appear here
                                when an auditable action occurs.
                            </p>

                        </div>

                    ) : (

                        <div className="timeline">

                            {history.map(
                                (item) => (

                                    <div
                                        className="timeline-item"
                                        key={
                                            item.recovery_id
                                        }
                                    >

                                        <div className="timeline-marker">

                                            <span />

                                        </div>


                                        <div className="timeline-content">

                                            <div className="timeline-header">

                                                <strong>
                                                    {
                                                        formatAction(
                                                            item.action
                                                        )
                                                    }
                                                </strong>


                                                <span
                                                    className={
                                                        `status-badge ${getStatusClass(
                                                            item.status
                                                        )}`
                                                    }
                                                >

                                                    {
                                                        item.status
                                                    }

                                                </span>

                                            </div>


                                            <p className="timeline-time">

                                                {
                                                    formatDate(
                                                        item.executed_at
                                                    )
                                                }

                                            </p>


                                            <p className="timeline-recovery">

                                                {Number(
                                                    item.amount_recovered
                                                ) > 0
                                                    ? `₹${Number(
                                                        item.amount_recovered
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )} recovered`
                                                    : "No amount recovered yet"}

                                            </p>


                                            <small>

                                                Recovery ID:{" "}
                                                {
                                                    item.recovery_id
                                                }

                                            </small>

                                        </div>

                                    </div>

                                )
                            )}

                        </div>

                    )}

                </div>

            </div>

        </div>

    );

}


/* =========================================
   HELPERS
========================================= */

function formatAction(action) {

    if (!action) {
        return "Recovery action";
    }

    return action
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            (letter) =>
                letter.toUpperCase()
        );

}


function formatDate(dateString) {

    if (!dateString) {
        return "Unknown time";
    }

    const date =
        new Date(dateString);

    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short",
        }
    );

}


function getStatusClass(status) {

    if (
        status === "recovered"
        || status === "executed"
    ) {
        return "status-recovered";
    }

    if (status === "failed") {
        return "status-failed";
    }

    return "status-default";

}

function getActionButtonLabel(
    action
) {

    if (action === "RETRY") {
        return "Execute Recovery";
    }

    if (action === "REMIND") {
        return "Send Reminder";
    }

    if (action === "CUSTOMER_ACTION") {
        return "Customer Action Required";
    }

    if (action === "ESCALATE") {
        return "Manual Review Required";
    }

    return "Action Unavailable";
}
export default TransactionPanel;