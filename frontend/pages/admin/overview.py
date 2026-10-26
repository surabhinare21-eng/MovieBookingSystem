
import streamlit as st

from api import PASSWORD_RULE

from common import (
    ROLE_LABELS,
    active_text,
    api,
    flash,
    matches,
    show_table,
    status_md,
    user_status_text,
)


def overview_page():
    ok_t, theatres, _ = api("GET", "/root-admin/theatres")
    ok_u, users, _ = api(
        "GET",
        "/root-admin/users",
        params={"limit": 200},
    )

    if not ok_t:
        st.error(theatres)
        return

    if not ok_u:
        st.error(users)
        return

    row1 = st.columns(3)
    row1[0].metric("Theatres", len(theatres))
    row1[1].metric(
        "Active theatres",
        sum(t["is_active"] for t in theatres),
    )
    row1[2].metric(
        "Inactive theatres",
        sum(not t["is_active"] for t in theatres),
    )

    row2 = st.columns(3)
    row2[0].metric(
        "Customers",
        sum(u["role"] == "CUSTOMER" for u in users),
    )
    row2[1].metric(
        "Theatre admins",
        sum(u["role"] == "ADMIN" for u in users),
    )
    row2[2].metric(
        "Blocked users",
        sum(not u["is_active"] for u in users),
    )

    if len(users) == 200:
        st.caption("User counts cover the first 200 users.")

    if not theatres:
        st.info(
            "No theatres yet. Open the Theatres tab "
            "to add the first one."
        )
    else:
        unassigned = [
            theatre
            for theatre in theatres
            if theatre["is_active"]
            and not any(
                user["role"] == "ADMIN"
                and user["theatre_id"] == theatre["theatre_id"]
                for user in users
            )
        ]

        if unassigned:
            st.warning(
                "Active theatres without a theatre admin: "
                + ", ".join(t["name"] for t in unassigned)
                + ". Create one in the Theatre admins tab."
            )


