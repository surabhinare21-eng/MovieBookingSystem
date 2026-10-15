
"""Shared helpers used by all Streamlit screens."""

from typing import Any

import streamlit as st

from api import DEFAULT_API_URL, call as api_call


ROLE_LABELS = {
    "SUPER_ADMIN": "Super admin",
    "ADMIN": "Theatre admin",
    "CUSTOMER": "Customer",
}


# --------------------------------------------------
# Session and notification helpers
# --------------------------------------------------

def flash(message: str) -> None:
    """Store a message to display after the next rerun."""
    st.session_state["flash"] = message


def log_out(notice: str | None = None) -> None:
    """Clear the current login session."""
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.session_state["notice"] = notice
    for key in list(st.session_state.keys()):
        if key.startswith("booking_"):
            del st.session_state[key]


# --------------------------------------------------
# Backend API helper
# --------------------------------------------------

def api(method: str, path: str, **kwargs: Any):
    """Call FastAPI using the configured URL and session token."""

    token_override = kwargs.pop("token_override", None)

    token = (
        token_override
        if token_override is not None
        else st.session_state.get("token")
    )

    api_url = st.session_state.get(
        "backend_url",
        DEFAULT_API_URL,
    )

    ok, data, code = api_call(
        method,
        api_url,
        path,
        token=token,
        **kwargs,
    )

    # Handle expired sessions or rejected authentication.
    if code == 401 and st.session_state.get("token"):
        log_out(
            "Your session expired or your account was blocked. "
            "Log in again."
        )
        st.rerun()

    return ok, data, code


# --------------------------------------------------
# Status helpers
# --------------------------------------------------

def status_color(value: str) -> str:
    """Return CSS styling for a status value."""
    if value == "Active":
        return "color: #1B7F3B; font-weight: 600"

    return "color: #B3261E; font-weight: 600"


def active_text(is_active: bool) -> str:
    """Return Active or Inactive."""
    return "Active" if is_active else "Inactive"


def user_status_text(is_active: bool) -> str:
    """Return Active or Blocked for a user account."""
    return "Active" if is_active else "Blocked"


def status_md(
    is_active: bool,
    off_word: str = "Inactive",
) -> str:
    """Return a colored Markdown status label."""
    return (
        ":green[Active]"
        if is_active
        else f":red[{off_word}]"
    )


# --------------------------------------------------
# Display helpers
# --------------------------------------------------

def show_table(
    rows: list[dict[str, Any]],
    columns: dict[str, str],
) -> None:
    """Display records using a field-to-label mapping."""

    if not rows:
        st.info("No records available.")
        return

    table_data = [
        {
            label: row.get(field, "-")
            for field, label in columns.items()
        }
        for row in rows
    ]

    st.dataframe(
        table_data,
        hide_index=True,
        width="stretch",
    )


def field(label: str, value: Any) -> None:
    """Display a labeled value."""
    st.caption(label)
    st.text(
        value if value not in (None, "") else "-"
    )


def status_field(
    label: str,
    is_active: bool,
    off_word: str = "Inactive",
) -> None:
    """Display a labeled, colored status."""
    st.caption(label)
    st.markdown(status_md(is_active, off_word))


# --------------------------------------------------
# Search helper
# --------------------------------------------------

def matches(query: str, *values: Any) -> bool:
    """Perform case-insensitive search across multiple values."""

    query = query.strip().casefold()

    if not query:
        return True

    return any(
        query in str(value).casefold()
        for value in values
        if value is not None
    )
