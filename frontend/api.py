import requests


DEFAULT_API_URL = "http://127.0.0.1:8000"


def post_json(api_url: str, path: str, payload: dict) -> tuple[bool, dict | str]:
    try:
        response = requests.post(
            f"{api_url.rstrip('/')}{path}",
            json=payload,
            timeout=10,
        )
    except requests.RequestException as exc:
        return False, f"Could not reach the backend: {exc}"

    try:
        body = response.json()
    except ValueError:
        body = response.text

    if not response.ok:
        if isinstance(body, dict):
            return False, str(body.get("detail", "Request failed."))
        return False, str(body)

    return True, body


def get_profile(api_url: str, token: str) -> tuple[bool, dict | str]:
    try:
        response = requests.get(
            f"{api_url.rstrip('/')}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException as exc:
        return False, f"Could not reach the backend: {exc}"

    body = response.json()
    if not response.ok:
        return False, str(body.get("detail", "Request failed."))
    return True, body
