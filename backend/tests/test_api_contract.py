import pytest

from backend.tests.conftest import (
    assert_json_response,
    fill_path_params,
    find_route,
)


def test_root_endpoint(client):
    response = client.get("/")
    data = assert_json_response(response)

    assert isinstance(data, dict)
    assert data.get("name")
    assert data.get("version")


def test_health_endpoint(client):
    response = client.get("/health")
    data = assert_json_response(response)

    assert isinstance(data, dict)
    assert data.get("status") == "healthy"
    assert data.get("service") == "recoveros-api"


@pytest.mark.parametrize(
    ("tokens", "expected_any_key"),
    [
        (("dashboard", "summary"), {
            "total_transactions",
            "failed_transactions",
            "recovered_transactions",
            "recovery_rate",
        }),
        (("opportunit",), {
            "opportunities",
        }),
        (("analytics", "overview"), {
            "total_transactions",
            "total_transaction_value",
            "failed_transactions",
            "recovered_amount",
        }),
    ],
)
def test_core_dashboard_get_routes(
    client,
    tokens,
    expected_any_key,
):
    path = find_route(*tokens, method="GET")
    response = client.get(path)
    data = assert_json_response(response)

    assert isinstance(data, dict)

    assert any(
        key in data
        for key in expected_any_key
    ), (
        f"{path} returned JSON, but none of the expected contract keys "
        f"were present. Got keys: {sorted(data.keys())}"
    )


def test_merchants_route_if_present(client):
    try:
        path = find_route("merchant", method="GET")
    except pytest.fail.Exception:
        pytest.skip("No merchant GET route is registered yet.")

    response = client.get(path)
    data = assert_json_response(response)

    assert isinstance(data, (dict, list))

    if isinstance(data, dict) and "merchants" in data:
        merchants = data["merchants"]
        assert isinstance(merchants, list)

        if merchants:
            first = merchants[0]
            assert isinstance(first, dict)
            assert "merchant_id" in first


def test_recovery_trend_route_if_present(client):
    try:
        path = find_route("trend", method="GET")
    except pytest.fail.Exception:
        pytest.skip("No recovery trend GET route is registered yet.")

    response = client.get(path)
    data = assert_json_response(response)

    assert isinstance(data, dict)
    assert "trends" in data
    assert isinstance(data["trends"], list)


def test_recovery_operations_route_if_present(client):
    try:
        path = find_route("operation", method="GET")
    except pytest.fail.Exception:
        pytest.skip("No recovery operations GET route is registered yet.")

    response = client.get(path, params={"limit": 20})
    data = assert_json_response(response)

    assert isinstance(data, dict)
    assert "summary" in data
    assert "activities" in data
    assert isinstance(data["activities"], list)


def test_known_manual_review_transaction_is_escalated(client):
    """
    Contract test for the Step-22 guardrail example.

    This is read-only: it analyses the transaction but does NOT execute
    a recovery action.
    """
    try:
        path_template = find_route(
            "transaction",
            method="GET",
            exclude=("history",),
        )
    except pytest.fail.Exception:
        pytest.skip("No transaction-analysis GET route is registered yet.")

    if "{" not in path_template:
        pytest.skip(
            "Transaction GET route does not expose a transaction-id path parameter."
        )

    path = fill_path_params(
        path_template,
        transaction_id="TXN-1007872",
        id="TXN-1007872",
        default="TXN-1007872",
    )

    response = client.get(path)

    if response.status_code == 404:
        pytest.skip(
            "Seed transaction TXN-1007872 is not present in this database."
        )

    data = assert_json_response(response)

    assert isinstance(data, dict)

    # Some route layouts return the analysis directly, while others may
    # wrap it. Keep the contract flexible but strict about the guardrail.
    decision = data.get("decision")

    if decision is None:
        pytest.skip(
            f"{path} is not the transaction-analysis endpoint "
            f"(returned keys: {sorted(data.keys())})."
        )

    assert decision.get("action") == "ESCALATE", (
        "Manual-review/non-recoverable transaction must not be recommended "
        f"for automatic execution. Decision was: {decision}"
    )

    transaction = data.get("transaction", {})

    if "requires_review" in transaction:
        assert transaction["requires_review"] is True

    if "is_recoverable" in transaction:
        assert transaction["is_recoverable"] is False


def test_openapi_exposes_recoveros_routes(client):
    response = client.get("/openapi.json")
    data = assert_json_response(response)

    paths = data.get("paths", {})
    assert isinstance(paths, dict)
    assert "/" in paths
    assert "/health" in paths

    recoveros_api_paths = [
        path
        for path in paths
        if path.startswith("/api/")
    ]

    assert len(recoveros_api_paths) >= 3, (
        "Expected RecoverOS API routes to be registered. "
        f"OpenAPI paths were: {sorted(paths)}"
    )
