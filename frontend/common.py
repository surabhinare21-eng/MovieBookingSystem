
"""Shared helpers used by all Streamlit screens."""

import streamlit as st

from api import DEFAULT_API_URL, call


ROLE_LABELS = {
    "SUPER_ADMIN": "Super admin",
    "ADMIN": "Theatre admin",
    "CUSTOMER": "Customer",
}


def flash(message: str) -> None:
    """Display a success message after the next rerun."""
    st.session_state.flash = message


def log_out(notice: str | None = None) -> None:
    """Clear the current login session."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.notice = notice


def api(method: str, path: str, **kwargs):
    """Call FastAPI using the configured URL and authentication token."""

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

    ok, data, code = call(
        method,
        api_url,
        path,
        token=token,
        **kwargs,
    )

    if code == 401 and st.session_state.get("token"):
        log_out(
            "Your session expired or your account was blocked. "
            "Log in again."
        )
        st.rerun()

    return ok, data, code


def status_color(value):
    """Return CSS styling for a status value."""
    if value == "Active":
        return "color: #1B7F3B; font-weight: 600"

    return "color: #B3261E; font-weight: 600"


def show_table(rows, columns: dict):
    """Display records using the specified field-to-label mapping."""
    if not rows:
        st.info("No records available.")
        return

    st.dataframe(
        [
            {
                label: row.get(field, "-")
                for field, label in columns.items()
            }
            for row in rows
        ],
        hide_index=True,
        width="stretch",
    )


def matches(query: str, *values) -> bool:
    """Case-insensitive search across multiple values."""
    query = query.strip().lower()

    return not query or any(
        query in str(value).lower()
        for value in values
    )


def active_text(is_active: bool) -> str:
    return "Active" if is_active else "Inactive"


def user_status_text(is_active: bool) -> str:
    return "Active" if is_active else "Blocked"


def status_md(
    is_active: bool,
    off_word: str = "Inactive",
) -> str:
    """Return a colored status label."""
    return (
        ":green[Active]"
        if is_active
        else f":red[{off_word}]"
    )


def field(label: str, value) -> None:
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