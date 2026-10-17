
"""Customer seat selection page."""

import streamlit as st

from common import api

MAX_SEATS = 10
GOLD_PRICE = 160
PLATINUM_PRICE = 180


def _seat_price(seat: dict) -> int:
    return PLATINUM_PRICE if str(seat.get("seat_type", "GOLD")).upper() == "PLATINUM" else GOLD_PRICE


@st.dialog("How many seats do you need?", width="small")
def choose_seat_count():
    count = st.selectbox(
        "Number of seats",
        options=list(range(0, MAX_SEATS + 1)),
        index=1,
        key="booking_seat_count_choice",
    )
    st.caption(f"Gold: ₹{GOLD_PRICE} per seat · Platinum: ₹{PLATINUM_PRICE} per seat")

    if st.button("Continue", type="primary", use_container_width=True):
        st.session_state["booking_requested_count"] = count
        st.session_state["booking_seat_ids"] = []
        st.session_state["booking_show_price_dialog"] = False
        st.rerun()


@st.dialog("Confirm your seats", width="small")
def confirm_seat_price(total: int, labels: list[str]):
    st.markdown(f"### Total price: ₹{total}")
    st.write("**Selected seats:** " + ", ".join(labels))
    st.caption("Your seats will be held for five minutes when you continue.")

    pay_col, back_col = st.columns(2)
    with pay_col:
        if st.button("Continue Payment", type="primary", use_container_width=True):
            show_id = st.session_state["booking_show_id"]
            selected_ids = st.session_state.get("booking_seat_ids", [])
            ok, result, status_code = api(
                "POST",
                "/seats/lock",
                json={"show_id": show_id, "seat_ids": selected_ids},
            )
            if ok:
                st.session_state["booking_lock_show_id"] = show_id
                st.session_state["booking_lock_seats"] = result
                st.session_state["booking_step"] = "payment"
                st.session_state["booking_show_price_dialog"] = False
                st.rerun()
            elif status_code == 409:
                st.session_state["booking_show_price_dialog"] = False
                st.session_state["booking_seat_ids"] = []
                st.error("One or more seats are no longer available. Please select again.")
                st.rerun()
            else:
                st.error(f"Unable to hold seats: {result}")

    with back_col:
        if st.button("Go Back", key="go_back_from_payment"):
            lock_show_id = st.session_state.get("booking_lock_show_id")
            locks = st.session_state.get("booking_lock_seats", [])

            if lock_show_id and locks:
                ok, result, status_code = api(
                    "POST",
                    "/seats/release",
                    json={
                        "show_id": lock_show_id,
                        "seat_ids": [
                            lock["seat_id"] for lock in locks
                        ],
                    },
                )

                if not ok:
                    st.error(f"Unable to release seats: {result}")
                    st.stop()

            # Clear the temporary booking state.
            st.session_state["booking_lock_show_id"] = None
            st.session_state["booking_lock_seats"] = []
            st.session_state["booking_seat_ids"] = []
            st.session_state["booking_step"] = "seats"

            st.rerun()


def seats_page():
    show_id = st.session_state.get("booking_show_id")
    if show_id is None:
        st.warning("Please select a show timing first.")
        return

    # The count dialog appears only after navigating to this dedicated page.
    if "booking_requested_count" not in st.session_state:
        choose_seat_count()
        return

    requested_count = st.session_state["booking_requested_count"]
    if requested_count == 0:
        st.info("You selected zero seats. Choose a positive number to select seats.")
        if st.button("Choose seat count again"):
            st.session_state.pop("booking_requested_count", None)
            st.rerun()
        return

    ok, seats, status_code = api("GET", f"/seats/show/{show_id}")
    if not ok:
        st.error(f"Unable to load seats: {seats}")
        st.caption(f"HTTP status: {status_code}")
        return
    if not seats:
        st.info("No seats have been generated for this screen yet.")
        return

    # Header: movie first, theatre immediately below it.
    st.title(st.session_state.get("booking_movie_title", "Selected Movie"))
    st.subheader(st.session_state.get("booking_theatre_name", "Selected Theatre"))

    seats_by_id = {seat["seat_id"]: seat for seat in seats}
    selected_ids = st.session_state.get("booking_seat_ids", [])
    selected_ids = [
        seat_id for seat_id in selected_ids
        if seat_id in seats_by_id
        and seats_by_id[seat_id].get("seat_status", "AVAILABLE") == "AVAILABLE"
    ]
    st.session_state["booking_seat_ids"] = selected_ids

    # Only customer-visible statuses; internal HOLD is deliberately not shown.
    st.markdown("🟢 Available　 ·　 🔴 Booked　 ·　 🔴 Selected")
    st.write(f"Select **{requested_count}** seat(s).")

    # Layout from the reference: Platinum rows first; Gold rows below.
    platinum_seats = [s for s in seats if str(s.get("seat_type", "GOLD")).upper() == "PLATINUM"]
    gold_seats = [s for s in seats if str(s.get("seat_type", "GOLD")).upper() != "PLATINUM"]

    def render_section(section_name: str, section_seats: list[dict]):
        if not section_seats:
            return
        st.markdown(f"### ₹{PLATINUM_PRICE} PLATINUM" if section_name == "PLATINUM" else f"### ₹{GOLD_PRICE} GOLD")
        row_numbers = sorted({s["row_no"] for s in section_seats}, reverse=True)
        for row_no in row_numbers:
            row_seats = sorted((s for s in section_seats if s["row_no"] == row_no), key=lambda s: s["col_no"])
            cols = st.columns(len(row_seats))
            for col, seat in zip(cols, row_seats):
                seat_id = seat["seat_id"]
                label = seat["seat_label"]
                status = str(seat.get("seat_status", "AVAILABLE")).upper()
                is_selected = seat_id in st.session_state["booking_seat_ids"]
                if status == "BOOKED":
                    icon, disabled = "🔴", True
                elif status == "HOLD":
                    # Held seats are unavailable; do not expose the internal HOLD status.
                    icon, disabled = "🔴", True
                elif is_selected:
                    icon, disabled = "Booked", False
                else:
                    icon, disabled = "🟢", False
                with col:
                    if st.button(f"{icon} {label}", key=f"seat_{show_id}_{seat_id}", disabled=disabled, use_container_width=True):
                        current = list(st.session_state["booking_seat_ids"])
                        if seat_id in current:
                            current.remove(seat_id)
                        elif len(current) < requested_count:
                            current.append(seat_id)
                        st.session_state["booking_seat_ids"] = current
                        if len(current) == requested_count:
                            st.session_state["booking_show_price_dialog"] = True
                        st.rerun()
        st.divider()

    render_section("PLATINUM", platinum_seats)
    render_section("GOLD", gold_seats)

    st.markdown("<div style='text-align:center;font-weight:700;padding:18px 0'>ALL EYES THIS WAY</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;border-radius:8px;background:#e8edf5;color:#1558a6;padding:16px'>SCREEN</div>", unsafe_allow_html=True)

    # No persistent booking summary: price is shown only in the final-seat popup.
    selected_seats = [seats_by_id[sid] for sid in st.session_state["booking_seat_ids"] if sid in seats_by_id]
    if st.session_state.get("booking_show_price_dialog") and len(selected_seats) == requested_count:
        total = sum(_seat_price(seat) for seat in selected_seats)
        labels = [seat["seat_label"] for seat in selected_seats]
        confirm_seat_price(total, labels)
