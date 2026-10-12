"""Small helper that every Streamlit screen uses to talk to the FastAPI backend."""

import requests

DEFAULT_API_URL = "http://127.0.0.1:8000"

PASSWORD_RULE = (
    "Password must be 8-12 characters and include an uppercase letter, "
    "a lowercase letter, a digit and one of @$!%*?&."
)


def _error_text(body, status_code: int) -> str:
    """Turn a FastAPI error body into one readable sentence."""
    if isinstance(body, dict):
        detail = body.get("detail")

        if isinstance(detail, str):
            return detail

        if isinstance(detail, list):
            parts = []
            for item in detail:
                field = ".".join(str(p) for p in item.get("loc", []) if p != "body")
                if item.get("type") == "string_pattern_mismatch" and field == "password":
                    message = PASSWORD_RULE
                else:
                    message = item.get("msg", "Invalid value")
                parts.append(f"{field}: {message}" if field else message)
            return " | ".join(parts)

    return f"Request failed (HTTP {status_code})."


def call(method, api_url, path, token=None, json=None, params=None):
    """
    Call the backend and return (ok, data_or_error_text, status_code).

    status_code is 0 when the backend could not be reached at all.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method,
            f"{api_url.rstrip('/')}{path}",
            headers=headers,
            json=json,
            params=params,
            timeout=10,
        )
    except requests.RequestException as exc:
        return False, f"Could not reach the backend at {api_url}: {exc}", 0

    try:
        body = response.json()
    except ValueError:
        body = response.text

    if not response.ok:
        return False, _error_text(body, response.status_code), response.status_code

    return True, body, response.status_code