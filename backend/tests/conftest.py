import re

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def get_openapi_paths():
    """
    Return the routes exposed by FastAPI's OpenAPI schema.

    Newer FastAPI versions may keep included routers internally as
    _IncludedRouter objects, which do not expose a .path attribute.
    OpenAPI is therefore the most stable source for route discovery.
    """
    schema = app.openapi()
    return schema.get("paths", {})


def find_route(*tokens, method="GET", exclude=()):
    """
    Find an API route by matching tokens against OpenAPI paths.
    """
    wanted = [str(token).lower() for token in tokens]
    blocked = [str(token).lower() for token in exclude]
    requested_method = method.lower()

    matches = []

    for path, operations in get_openapi_paths().items():
        lower_path = path.lower()

        if requested_method not in {
            operation.lower()
            for operation in operations.keys()
        }:
            continue

        if not all(token in lower_path for token in wanted):
            continue

        if any(token in lower_path for token in blocked):
            continue

        matches.append(path)

    if not matches:
        pytest.fail(
            "Could not find a "
            f"{method.upper()} route containing tokens {wanted}. "
            "Available OpenAPI routes: "
            + ", ".join(sorted(get_openapi_paths().keys()))
        )

    return sorted(
        matches,
        key=lambda value: (
            value.count("{"),
            len(value),
        ),
    )[0]


def fill_path_params(path, **known_values):
    """
    Replace FastAPI path parameters with supplied values.
    """
    def replacement(match):
        name = match.group(1)
        return str(
            known_values.get(
                name,
                known_values.get("default", "TEST"),
            )
        )

    return re.sub(
        r"\{([^}:]+)(?::[^}]+)?\}",
        replacement,
        path,
    )


def assert_json_response(response, expected_status=200):
    assert response.status_code == expected_status, (
        f"Expected HTTP {expected_status}, "
        f"got {response.status_code}. "
        f"Response: {response.text}"
    )

    content_type = response.headers.get(
        "content-type",
        "",
    )

    assert "application/json" in content_type.lower(), (
        "Expected JSON response, "
        f"got content-type {content_type!r}"
    )

    return response.json()
