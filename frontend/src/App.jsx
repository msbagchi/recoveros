import {
    useEffect,
    useState,
} from "react";

import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";

import TransactionPanel
    from "./components/TransactionPanel";

import RecoveryOperations
    from "./components/RecoveryOperations";

import PromiseTracker
    from "./components/PromiseTracker";

import EscalationQueue
    from "./components/EscalationQueue";

import BatchRecovery
    from "./components/BatchRecovery";

import CheckoutAbandonment
    from "./components/CheckoutAbandonment";

import SubscriptionRecovery
    from "./components/SubscriptionRecovery";

import MandateRetry
    from "./components/MandateRetry";

import B2BReceivables
    from "./components/B2BReceivables";

import {
    getMerchants,
    getDashboardSummary,
    getOpportunities,
    getAnalyticsOverview,
    getRecoveryTrends,
    getStoppingRules,
    getRecoveryImpact,
} from "./services/api";

import "./index.css";


const TABS = [
    { id: "dashboard",   label: "Dashboard"   },
    { id: "promises",    label: "Promises"    },
    { id: "escalations", label: "Escalations" },
    { id: "workflows",   label: "Workflows"   },
];

const WORKFLOW_TABS = [
    { id: "checkout",      label: "Checkout Abandonment"  },
    { id: "subscription",  label: "Subscription Recovery" },
    { id: "mandate",       label: "Mandate Retry"         },
    { id: "b2b",           label: "B2B Receivables"       },
];


function App() {

    const [merchants, setMerchants] =
        useState([]);

    const [
        selectedMerchant,
        setSelectedMerchant,
    ] = useState("");

    const [activeTab, setActiveTab] =
        useState("dashboard");

    const [summary, setSummary] =
        useState(null);

    const [analytics, setAnalytics] =
        useState(null);

    const [trends, setTrends] =
        useState([]);

    const [
        opportunities,
        setOpportunities,
    ] = useState([]);

    const [
        priorityFilter,
        setPriorityFilter,
    ] = useState("ALL");

    const [loading, setLoading] =
        useState(true);

    const [refreshing, setRefreshing] =
        useState(false);

    const [error, setError] =
        useState(null);

    const [
        selectedTransaction,
        setSelectedTransaction,
    ] = useState(null);

    const [reloadKey, setReloadKey] =
        useState(0);

    const [activeWorkflow, setActiveWorkflow] =
        useState("checkout");

    const [stoppingRules, setStoppingRules] =
        useState(null);

    const [impact, setImpact] =
        useState(null);


    // =========================================
    // LOAD MERCHANTS
    // =========================================

    useEffect(() => {

        async function loadMerchants() {

            try {

                const data =
                    await getMerchants();

                setMerchants(
                    data.merchants || []
                );

            } catch (err) {

                console.error(
                    "Merchant loading error:",
                    err
                );

            }

        }

        loadMerchants();

    }, []);


    // =========================================
    // LOAD STOPPING RULES (once)
    // =========================================

    useEffect(() => {

        getStoppingRules()
            .then(setStoppingRules)
            .catch(console.error);

    }, []);


    // =========================================
    // LOAD DASHBOARD
    // =========================================

    useEffect(() => {

        let active = true;

        async function loadDashboard() {

            try {

                setError(null);

                if (analytics) {
                    setRefreshing(true);
                } else {
                    setLoading(true);
                }

                const merchantId =
                    selectedMerchant || null;

                const [
                    summaryData,
                    opportunityData,
                    analyticsData,
                    trendData,
                    impactData,
                ] = await Promise.all([

                    getDashboardSummary(
                        merchantId
                    ),

                    getOpportunities(
                        10,
                        merchantId
                    ),

                    getAnalyticsOverview(
                        merchantId
                    ),

                    getRecoveryTrends(
                        merchantId
                    ),

                    getRecoveryImpact(
                        merchantId
                    ),

                ]);

                if (!active) {
                    return;
                }

                setSummary(
                    summaryData
                );

                setOpportunities(
                    opportunityData
                        .opportunities || []
                );

                setAnalytics(
                    analyticsData
                );

                setTrends(
                    trendData.trends || []
                );

                setImpact(impactData);

                setPriorityFilter(
                    "ALL"
                );

                setSelectedTransaction(
                    null
                );

            } catch (err) {

                console.error(
                    "Dashboard loading error:",
                    err
                );

                if (active) {

                    setError(
                        "Unable to load RecoverOS dashboard."
                    );

                }

            } finally {

                if (active) {

                    setLoading(false);
                    setRefreshing(false);

                }

            }

        }

        loadDashboard();

        return () => {
            active = false;
        };

    }, [
        selectedMerchant,
        reloadKey,
    ]);


    // =========================================
    // FILTER OPPORTUNITIES
    // =========================================

    const filteredOpportunities =
        priorityFilter === "ALL"
            ? opportunities
            : opportunities.filter(
                (item) =>
                    String(
                        item.priority || ""
                    ).toUpperCase() ===
                    priorityFilter
            );


    const selectedMerchantName =
        selectedMerchant
            ? merchants.find(
                (merchant) =>
                    merchant.merchant_id ===
                    selectedMerchant
            )?.name || selectedMerchant
            : "All Merchants";


    // =========================================
    // INITIAL LOADING
    // =========================================

    if (loading) {

        return (
            <div className="app-state-screen">

                <div className="app-state-card">

                    <div className="loading-spinner" />

                    <p className="eyebrow">
                        RECOVEROS
                    </p>

                    <h2>
                        Preparing recovery intelligence
                    </h2>

                    <p>
                        Loading transactions, recovery
                        opportunities and analytics.
                    </p>

                </div>

            </div>
        );

    }


    if (error && !analytics) {

        return (
            <div className="app-state-screen">

                <div className="app-state-card error-state">

                    <div className="state-symbol">
                        !
                    </div>

                    <p className="eyebrow">
                        CONNECTION ERROR
                    </p>

                    <h2>
                        RecoverOS couldn't load
                        the dashboard
                    </h2>

                    <p>
                        {error}
                    </p>

                    <button
                        className="retry-button"
                        onClick={() =>
                            setReloadKey(
                                (value) => value + 1
                            )
                        }
                    >
                        Retry dashboard
                    </button>

                </div>

            </div>
        );

    }


    return (

        <div className="app">

            {/* =================================
                TOP BAR
            ================================= */}

            <header className="topbar">

                <div>

                    <h1>
                        RecoverOS
                    </h1>

                    <p>
                        Revenue recovery intelligence
                    </p>

                </div>


                <div className="topbar-actions">

                    <div className="merchant-selector">

                        <label
                            htmlFor="merchant-select"
                        >
                            Merchant
                        </label>

                        <select
                            id="merchant-select"
                            value={
                                selectedMerchant
                            }
                            onChange={(event) =>
                                setSelectedMerchant(
                                    event.target.value
                                )
                            }
                            disabled={refreshing}
                        >

                            <option value="">
                                All Merchants
                            </option>

                            {merchants.map(
                                (merchant) => (

                                    <option
                                        key={
                                            merchant.merchant_id
                                        }
                                        value={
                                            merchant.merchant_id
                                        }
                                    >
                                        {merchant.name}
                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    <div className="status">

                        <span></span>

                        System operational

                    </div>

                </div>

            </header>


            {/* =================================
                TAB NAVIGATION
            ================================= */}

            <nav className="tab-bar">

                {TABS.map(({ id, label }) => (

                    <button
                        key={id}
                        className={
                            `tab-button${
                                activeTab === id
                                    ? " active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            setActiveTab(id)
                        }
                    >
                        {label}
                    </button>

                ))}

            </nav>


            <main className="content">

                {refreshing &&
                    activeTab === "dashboard" && (

                    <div className="refresh-indicator">

                        <div className="refresh-spinner" />

                        <span>
                            Updating data for{" "}
                            <strong>
                                {selectedMerchantName}
                            </strong>
                        </span>

                    </div>

                )}


                {/* =================================
                    DASHBOARD TAB
                ================================= */}

                {activeTab === "dashboard" && (

                    <>

                        {/* =====================
                            HERO
                        ===================== */}

                        <section className="hero">

                            <div>

                                <p className="eyebrow">
                                    RECOVERY CONTROL CENTER
                                </p>

                                <h2>
                                    Don't let failed payments
                                    become lost revenue.
                                </h2>

                                <p>
                                    RecoverOS identifies the
                                    payment failures worth acting
                                    on and recommends the safest
                                    next step.
                                </p>

                            </div>


                            <div className="merchant-context">

                                <span>
                                    Viewing
                                </span>

                                <strong>
                                    {selectedMerchantName}
                                </strong>

                                {refreshing && (
                                    <small>
                                        Updating dashboard...
                                    </small>
                                )}

                            </div>

                        </section>


                        {error && (

                            <div className="dashboard-warning">

                                <div>
                                    <strong>
                                        Dashboard update failed
                                    </strong>

                                    <span>
                                        {error}
                                    </span>
                                </div>

                                <button
                                    onClick={() =>
                                        setReloadKey(
                                            (value) => value + 1
                                        )
                                    }
                                >
                                    Retry
                                </button>

                            </div>

                        )}


                        {/* =====================
                            IMPACT METRICS
                        ===================== */}

                        {impact && (

                            <section className="metrics">

                                <div className="metric">
                                    <span>
                                        Total transaction value
                                    </span>
                                    <strong>
                                        ₹
                                        {Number(
                                            analytics
                                                ?.total_transaction_value ??
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

                                <div className="metric">
                                    <span>
                                        Failed payment value
                                    </span>
                                    <strong>
                                        ₹
                                        {Number(
                                            analytics
                                                ?.failed_transaction_value ??
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

                                <div className="metric">
                                    <span>
                                        Batch potential recovery
                                    </span>
                                    <strong>
                                        ₹
                                        {Number(
                                            impact
                                                ?.batch_potential_amount ??
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

                                <div className="metric">
                                    <span>
                                        Escalations pending
                                    </span>
                                    <strong>
                                        {
                                            impact
                                                ?.escalations_pending ??
                                            0
                                        }
                                    </strong>
                                </div>

                            </section>

                        )}


                        {/* =====================
                            SECONDARY ANALYTICS
                        ===================== */}

                        <section className="analytics-grid">

                            <div className="analytics-card">
                                <span>
                                    Total transactions
                                </span>
                                <strong>
                                    {
                                        summary
                                            ?.total_transactions ??
                                        0
                                    }
                                </strong>
                                <small>
                                    Payments processed
                                </small>
                            </div>

                            <div className="analytics-card">
                                <span>
                                    Failed transactions
                                </span>
                                <strong>
                                    {
                                        analytics
                                            ?.failed_transactions ??
                                        0
                                    }
                                </strong>
                                <small>
                                    Transactions requiring attention
                                </small>
                            </div>

                            <div className="analytics-card">
                                <span>
                                    Recoverable transactions
                                </span>
                                <strong>
                                    {
                                        analytics
                                            ?.recoverable_transactions ??
                                        0
                                    }
                                </strong>
                                <small>
                                    Currently eligible for recovery
                                </small>
                            </div>

                            <div className="analytics-card">
                                <span>
                                    Recoverable value
                                </span>
                                <strong>
                                    ₹
                                    {Number(
                                        analytics
                                            ?.recoverable_value ??
                                        0
                                    ).toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        }
                                    )}
                                </strong>
                                <small>
                                    Value identified as recoverable
                                </small>
                            </div>

                            <div className="analytics-card">
                                <span>
                                    Batch runs
                                </span>
                                <strong>
                                    {
                                        impact
                                            ?.batch_runs_total ??
                                        0
                                    }
                                </strong>
                                <small>
                                    Total batch recovery runs
                                </small>
                            </div>

                        </section>


                        {/* =====================
                            COMPLIANCE CONFIG
                        ===================== */}

                        {stoppingRules && (

                            <section className="compliance-section">

                                <div className="section-heading">

                                    <div>

                                        <p className="eyebrow">
                                            COMPLIANCE CONFIG
                                        </p>

                                        <h2>
                                            Active stopping rules
                                        </h2>

                                    </div>

                                    <span className="compliance-active-badge">
                                        Active
                                    </span>

                                </div>

                                <div className="compliance-grid">

                                    <div className="compliance-rule">
                                        <span>
                                            Max attempts
                                        </span>
                                        <strong>
                                            {
                                                stoppingRules.max_attempt_number
                                            }
                                        </strong>
                                        <small>
                                            Auto-retry limit per transaction
                                        </small>
                                    </div>

                                    <div className="compliance-rule">
                                        <span>
                                            Min amount
                                        </span>
                                        <strong>
                                            ₹
                                            {
                                                stoppingRules.min_recoverable_amount
                                            }
                                        </strong>
                                        <small>
                                            Minimum recoverable threshold
                                        </small>
                                    </div>

                                    <div className="compliance-rule">
                                        <span>
                                            Blocked reasons
                                        </span>
                                        <strong>
                                            {
                                                stoppingRules
                                                    .blocked_failure_reasons
                                                    ?.length ?? 0
                                            }
                                        </strong>
                                        <small>
                                            {stoppingRules
                                                .blocked_failure_reasons
                                                ?.join(", ")}
                                        </small>
                                    </div>

                                </div>

                            </section>

                        )}


                        {/* =====================
                            BATCH RECOVERY
                        ===================== */}

                        <BatchRecovery
                            merchantId={
                                selectedMerchant ||
                                null
                            }
                        />


                        {/* =====================
                            RECOVERY TREND
                        ===================== */}

                        <section className="chart-section">

                            <div className="section-heading">

                                <div>

                                    <p className="eyebrow">
                                        PERFORMANCE
                                    </p>

                                    <h2>
                                        Recovery trend
                                    </h2>

                                </div>

                            </div>


                            <div className="chart-card">

                                {trends.length === 0 ? (

                                    <div className="empty-state">
                                        No recovery trend data
                                        for this merchant.
                                    </div>

                                ) : (

                                    <ResponsiveContainer
                                        width="100%"
                                        height={320}
                                    >

                                        <LineChart
                                            data={trends}
                                        >

                                            <CartesianGrid
                                                strokeDasharray="3 3"
                                            />

                                            <XAxis
                                                dataKey="date"
                                            />

                                            <YAxis />

                                            <Tooltip />

                                            <Legend />

                                            <Line
                                                type="monotone"
                                                dataKey={
                                                    "successful_recoveries"
                                                }
                                                name={
                                                    "Successful recoveries"
                                                }
                                                strokeWidth={3}
                                                dot={true}
                                            />

                                            <Line
                                                type="monotone"
                                                dataKey={
                                                    "failed_recoveries"
                                                }
                                                name={
                                                    "Failed recoveries"
                                                }
                                                strokeWidth={2}
                                                dot={true}
                                            />

                                            <Line
                                                type="monotone"
                                                dataKey={
                                                    "executed_actions"
                                                }
                                                name={
                                                    "Simulated executions"
                                                }
                                                strokeWidth={2}
                                                dot={true}
                                            />

                                        </LineChart>

                                    </ResponsiveContainer>

                                )}

                            </div>

                        </section>


                        {/* =====================
                            RECOVERED REVENUE
                        ===================== */}

                        <section className="chart-section">

                            <div className="section-heading">

                                <div>

                                    <p className="eyebrow">
                                        REVENUE IMPACT
                                    </p>

                                    <h2>
                                        Recovered revenue
                                    </h2>

                                </div>

                            </div>


                            <div className="chart-card">

                                {trends.length === 0 ? (

                                    <div className="empty-state">
                                        No recovered revenue data.
                                    </div>

                                ) : (

                                    <ResponsiveContainer
                                        width="100%"
                                        height={320}
                                    >

                                        <BarChart
                                            data={trends}
                                        >

                                            <CartesianGrid
                                                strokeDasharray="3 3"
                                            />

                                            <XAxis
                                                dataKey="date"
                                            />

                                            <YAxis />

                                            <Tooltip />

                                            <Legend />

                                            <Bar
                                                dataKey={
                                                    "recovered_amount"
                                                }
                                                name={
                                                    "Recovered amount"
                                                }
                                            />

                                        </BarChart>

                                    </ResponsiveContainer>

                                )}

                            </div>

                        </section>


                        {/* =====================
                            OPPORTUNITIES
                        ===================== */}

                        <section className="opportunities">

                            <div className="section-heading">

                                <div>

                                    <p className="eyebrow">
                                        PRIORITY QUEUE
                                    </p>

                                    <h2>
                                        Recovery opportunities
                                    </h2>

                                </div>


                                <span>
                                    {
                                        filteredOpportunities.length
                                    }
                                    {" "}
                                    shown
                                </span>

                            </div>


                            <div className="opportunity-filters">

                                {[
                                    "ALL",
                                    "HIGH",
                                    "MEDIUM",
                                    "LOW",
                                ].map((filter) => (

                                    <button
                                        key={filter}
                                        className={
                                            priorityFilter ===
                                            filter
                                                ? "filter-button active"
                                                : "filter-button"
                                        }
                                        onClick={() =>
                                            setPriorityFilter(
                                                filter
                                            )
                                        }
                                    >
                                        {filter}
                                    </button>

                                ))}

                            </div>


                            <div className="table-wrapper">

                                <table>

                                    <thead>

                                        <tr>

                                            <th>
                                                Transaction
                                            </th>

                                            <th>
                                                Amount
                                            </th>

                                            <th>
                                                Recovery chance
                                            </th>

                                            <th>
                                                Expected recovery
                                            </th>

                                            <th>
                                                Priority
                                            </th>

                                            <th>
                                                Action
                                            </th>

                                        </tr>

                                    </thead>


                                    <tbody>

                                        {
                                            filteredOpportunities
                                                .length === 0
                                                ? (

                                                    <tr>

                                                        <td
                                                            colSpan="6"
                                                            className="empty-state"
                                                        >
                                                            <div className="table-empty-content">

                                                                <strong>
                                                                    No recovery opportunities
                                                                </strong>

                                                                <span>
                                                                    No transactions match the
                                                                    selected merchant and priority
                                                                    filter.
                                                                </span>

                                                            </div>
                                                        </td>

                                                    </tr>

                                                )
                                                : (

                                                    filteredOpportunities
                                                        .map(
                                                            (item) => (

                                                                <tr
                                                                    key={
                                                                        item.transaction_id
                                                                    }
                                                                >

                                                                    <td>

                                                                        <button
                                                                            className="transaction-link"
                                                                            onClick={() =>
                                                                                setSelectedTransaction(
                                                                                    item.transaction_id
                                                                                )
                                                                            }
                                                                        >
                                                                            {
                                                                                item.transaction_id
                                                                            }
                                                                        </button>

                                                                    </td>


                                                                    <td>
                                                                        ₹
                                                                        {Number(
                                                                            item.amount ??
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

                                                                        <div className="probability-cell">

                                                                            <div className="probability-bar">

                                                                                <div
                                                                                    className="probability-fill"
                                                                                    style={{
                                                                                        width: `${Math.min(
                                                                                            Number(
                                                                                                item.ml_probability ??
                                                                                                0
                                                                                            ) *
                                                                                            100,
                                                                                            100
                                                                                        )}%`,
                                                                                    }}
                                                                                />

                                                                            </div>

                                                                            <span>
                                                                                {(
                                                                                    Number(
                                                                                        item.ml_probability ??
                                                                                        0
                                                                                    ) *
                                                                                    100
                                                                                ).toFixed(
                                                                                    1
                                                                                )}
                                                                                %
                                                                            </span>

                                                                        </div>

                                                                    </td>


                                                                    <td>
                                                                        ₹
                                                                        {Number(
                                                                            item.expected_recovery ??
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
                                                                                `priority-badge priority-${String(
                                                                                    item.priority ||
                                                                                    "LOW"
                                                                                ).toLowerCase()}`
                                                                            }
                                                                        >
                                                                            {
                                                                                item.priority ||
                                                                                "LOW"
                                                                            }
                                                                        </span>

                                                                    </td>


                                                                    <td>

                                                                        <span
                                                                            className={
                                                                                `action ${String(
                                                                                    item.recommended_action ||
                                                                                    ""
                                                                                ).toLowerCase()}`
                                                                            }
                                                                        >
                                                                            {
                                                                                item.recommended_action ||
                                                                                "REVIEW"
                                                                            }
                                                                        </span>

                                                                    </td>

                                                                </tr>

                                                            )
                                                        )

                                                )
                                        }

                                    </tbody>

                                </table>

                            </div>

                        </section>


                        {/* =====================
                            RECOVERY OPERATIONS
                        ===================== */}

                        <RecoveryOperations
                            merchantId={
                                selectedMerchant ||
                                null
                            }
                        />

                    </>

                )}


                {/* =================================
                    PROMISES TAB
                ================================= */}

                {activeTab === "promises" && (

                    <PromiseTracker
                        merchantId={
                            selectedMerchant ||
                            null
                        }
                    />

                )}


                {/* =================================
                    ESCALATIONS TAB
                ================================= */}

                {activeTab === "escalations" && (

                    <EscalationQueue
                        merchantId={
                            selectedMerchant ||
                            null
                        }
                    />

                )}


                {/* =================================
                    WORKFLOWS TAB
                ================================= */}

                {activeTab === "workflows" && (

                    <div className="workflows-container">

                        <div className="workflows-header">

                            <div>
                                <p className="eyebrow">
                                    TRACK 03 — EXAMPLE DIRECTIONS
                                </p>
                                <h2>
                                    Specialized recovery workflows
                                </h2>
                            </div>

                        </div>

                        <nav className="workflow-tab-bar">

                            {WORKFLOW_TABS.map(
                                ({ id, label }) => (

                                    <button
                                        key={id}
                                        className={
                                            `workflow-tab-btn${
                                                activeWorkflow === id
                                                    ? " active"
                                                    : ""
                                            }`
                                        }
                                        onClick={() =>
                                            setActiveWorkflow(id)
                                        }
                                    >
                                        {label}
                                    </button>

                                )
                            )}

                        </nav>

                        {activeWorkflow === "checkout" && (
                            <CheckoutAbandonment
                                merchantId={
                                    selectedMerchant || null
                                }
                            />
                        )}

                        {activeWorkflow === "subscription" && (
                            <SubscriptionRecovery
                                merchantId={
                                    selectedMerchant || null
                                }
                            />
                        )}

                        {activeWorkflow === "mandate" && (
                            <MandateRetry
                                merchantId={
                                    selectedMerchant || null
                                }
                            />
                        )}

                        {activeWorkflow === "b2b" && (
                            <B2BReceivables
                                merchantId={
                                    selectedMerchant || null
                                }
                            />
                        )}

                    </div>

                )}

            </main>


            {/* =================================
                TRANSACTION PANEL
            ================================= */}

            {selectedTransaction && (

                <TransactionPanel
                    transactionId={
                        selectedTransaction
                    }
                    onClose={() =>
                        setSelectedTransaction(
                            null
                        )
                    }
                />

            )}

        </div>

    );

}


export default App;
