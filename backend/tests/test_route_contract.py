from backend.tests.conftest import (
    find_route,
    get_openapi_paths,
)


def test_expected_dashboard_routes_are_registered():
    assert "dashboard" in find_route(
        "dashboard",
        "summary",
        method="GET",
    ).lower()

    assert "opportunit" in find_route(
        "opportunit",
        method="GET",
    ).lower()

    assert "analytics" in find_route(
        "analytics",
        "overview",
        method="GET",
    ).lower()


def test_no_duplicate_openapi_operation_pairs():
    """
    OpenAPI cannot contain two separately-addressable operations
    with the same HTTP method and path. Validate the generated
    contract instead of relying on FastAPI's internal route objects.
    """
    paths = get_openapi_paths()
    seen = set()
    duplicates = []

    for path, operations in paths.items():
        for method in operations:
            method_upper = method.upper()

            if method_upper not in {
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            }:
                continue

            pair = (
                method_upper,
                path,
            )

            if pair in seen:
                duplicates.append(pair)
            else:
                seen.add(pair)

    assert not duplicates, (
        "Duplicate API operations found: "
        + ", ".join(
            f"{method} {path}"
            for method, path in duplicates
        )
    )
