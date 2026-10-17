"""Customer seat-selection page for the MovieBookingSystem."""

import streamlit as st

from common import api

MAX_SEATS = 10
GOLD_PRICE = 160
PLATINUM_PRICE = 180


def _clear_seat_selection() -> None:
    st.session_state["booking_seat_ids"] = []
    st.session_state["booking_seat_count"] = None
    st.session_state["booking_show_seat_dialog"] = True
    st.session_state["booking_show_confirm_dialog"] = False


@st.dialog("How many seats?")
def _seat_count_dialog() -> None:
    """Ask how many seats the customer wants before showing the layout."""

    st.write("Select the number of seats")

    count = st.radio(
        "Number of seats",
        options=list(range(1, MAX_SEATS + 1)),
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="booking_seat_count_radio",
    )

    st.divider()
    gold_col, platinum_col = st.columns(2)
    with gold_col:
        st.write("GOLD")
        st.markdown(f"**₹{GOLD_PRICE}**")
    with platinum_col:
        st.write("PLATINUM")
        st.markdown(f"**₹{PLATINUM_PRICE}**")

    if st.button("Continue", type="primary", use_container_width=True,
                  key="confirm_seat_count"):
        st.session_state["booking_seat_count"] = count
        st.session_state["booking_seat_ids"] = []
        st.session_state["booking_show_seat_dialog"] = False
        st.rerun()


@st.dialog("Confirm your seats")
def _seat_confirmation_dialog(selected_seats: list[dict], show_id: int) -> None:
    """Show the total after the customer selects the requested number of seats."""

    selected_labels = ", ".join(seat["seat_label"] for seat in selected_seats)
    total = sum(
        PLATINUM_PRICE if seat["seat_type"].upper() == "PLATINUM"
        else GOLD_PRICE
        for seat in selected_seats
    )

    st.markdown(f"**Total price: ₹{total}**")
    st.markdown(f"**Selected seats:** {selected_labels}")
    st.caption("Your seats will be held for five minutes when you continue.")

    pay_col, back_col = st.columns(2)

    with pay_col:
        continue_payment = st.button(
            "Continue Payment",
            type="primary",
            use_container_width=True,
            key="continue_seat_payment",
        )

    with back_col:
        go_back = st.button(
            "Go Back",
            use_container_width=True,
            key="back_from_seat_confirmation",
        )

    if go_back:
        # Close the price dialog and return to the same layout.
        # Keep the selected seats highlighted so the customer can adjust them.
        st.session_state["booking_show_confirm_dialog"] = False
        st.rerun()

    if continue_payment:
        ok, result, status_code = api(
            "POST",
            "/seats/lock",
            json={
                "show_id": show_id,
                "seat_ids": [seat["seat_id"] for seat in selected_seats],
            },
        )

        if ok:
            st.session_state["booking_lock_show_id"] = show_id
            st.session_state["booking_lock_seats"] = result
            st.session_state["booking_step"] = "payment"
            st.session_state["booking_show_confirm_dialog"] = False
            st.success("Seats held successfully for five minutes.")
            st.rerun()
        elif status_code == 409:
            st.error(
                "One or more seats are no longer available. "
                "Please choose your seats again."
            )
            st.session_state["booking_seat_ids"] = []
            st.session_state["booking_show_confirm_dialog"] = False
            st.rerun()
        else:
            st.error(f"Unable to hold seats: {result}")
            st.caption(f"HTTP status: {status_code}")


def seats_page() -> None:
    st.subheader("Select Your Seats")
    st.caption("Choose your seats. Temporary holds are not shown as booked.")

    # Keep the back control at the top-left of the page.
    if st.button("← Back to show timings", key="back_to_show_timings_top"):
        st.session_state["booking_step"] = "theatres"
        st.session_state["booking_seat_ids"] = []
        st.session_state["booking_seat_count"] = None
        st.session_state["booking_show_seat_dialog"] = False
        st.session_state["booking_show_confirm_dialog"] = False
        st.rerun()

    show_id = st.session_state.get("booking_show_id")
    if show_id is None:
        st.warning("Please select a show timing first.")
        return

    ok, seats, status_code = api("GET", f"/seats/show/{show_id}")
    if not ok:
        st.error(f"Unable to load seats: {seats}")
        st.caption(f"HTTP status: {status_code}")
        return

    if not seats:
        st.info("No seats have been generated for this screen yet.")
        return

    # Show name metadata when the show-selection page has saved it.
    st.markdown("### " + str(st.session_state.get("booking_movie_title", "Selected Movie")))
    st.markdown("#### " + str(st.session_state.get("booking_theatre_name", "Selected Theatre")))

    seats_by_id = {int(seat["seat_id"]): seat for seat in seats}

    if "booking_seat_ids" not in st.session_state:
        st.session_state["booking_seat_ids"] = []

    if "booking_seat_count" not in st.session_state:
        st.session_state["booking_seat_count"] = None

    if "booking_show_seat_dialog" not in st.session_state:
        st.session_state["booking_show_seat_dialog"] = True

    if "booking_show_confirm_dialog" not in st.session_state:
        st.session_state["booking_show_confirm_dialog"] = False

    # On first entry to this show, ask for the required seat count.
    if st.session_state["booking_seat_count"] is None:
        st.session_state["booking_show_seat_dialog"] = True

    if st.session_state["booking_show_seat_dialog"]:
        _seat_count_dialog()
        return

    st.markdown("🟢 Available  ·  🔴 Booked  ·  🔴 Selected")
    required_count = int(st.session_state["booking_seat_count"])
    st.caption(
        f"Select {required_count} seat(s).  "
        f"Selected: {len(st.session_state['booking_seat_ids'])}/{required_count}"
    )

    selected_ids = st.session_state["booking_seat_ids"]
    # Remove locally selected seats if another user has since booked/held them.
    selected_ids[:] = [
        seat_id for seat_id in selected_ids
        if seat_id in seats_by_id
        and seats_by_id[seat_id].get("seat_status") == "AVAILABLE"
    ]
    st.session_state["booking_seat_ids"] = selected_ids

    # Group seats by category, matching the reference layout: Platinum first,
    # then Gold. Within each category, keep rows and columns in screen order.
    for category, price in (("PLATINUM", PLATINUM_PRICE), ("GOLD", GOLD_PRICE)):
        category_seats = [
            seat for seat in seats
            if str(seat.get("seat_type", "GOLD")).upper() == category
        ]
        if not category_seats:
            continue

        st.markdown(f"### ₹{price} {category}")
        category_rows = sorted({seat["row_no"] for seat in category_seats})

        for row_no in category_rows:
            row_seats = sorted(
                [seat for seat in category_seats if seat["row_no"] == row_no],
                key=lambda seat: seat["col_no"],
            )
            row_label = row_seats[0]["seat_label"][0]
            row_label_col, *seat_columns = st.columns([0.5] + [1] * len(row_seats))
            row_label_col.markdown(f"**{row_label}**")

            for column, seat in zip(seat_columns, row_seats):
                seat_id = int(seat["seat_id"])
                label = seat["seat_label"]
                seat_status = seat.get("seat_status", "AVAILABLE")
                is_selected = seat_id in selected_ids

                # Selected seats are highlighted red, like the reference image.
                button_type = "primary" if is_selected else "secondary"
                disabled = seat_status != "AVAILABLE" and not is_selected
                icon = "🔴" if (seat_status == "BOOKED" or is_selected) else "🟢"

                with column:
                    if st.button(
                        f"{icon} {label}",
                        key=f"seat_{show_id}_{seat_id}",
                        type=button_type,
                        disabled=disabled,
                        use_container_width=True,
                    ):
                        if seat_id in selected_ids:
                            selected_ids.remove(seat_id)
                        elif len(selected_ids) < required_count:
                            selected_ids.append(seat_id)

                        st.session_state["booking_seat_ids"] = selected_ids

                        if len(selected_ids) == required_count:
                            st.session_state["booking_show_confirm_dialog"] = True
                        else:
                            st.session_state["booking_show_confirm_dialog"] = False
                        st.rerun()

    # Screen bar belongs at the very bottom, with the centered label directly above.
    st.divider()
    st.markdown(
        "<div style='text-align:center; font-weight:600; margin: 0.5rem 0 1rem;'>"
        "ALL EYES THIS WAY</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='background:#e8f1ff; color:#0756a5; padding:1rem 1.5rem; "
        "border-radius:0.6rem; text-align:center; font-weight:600;'>SCREEN</div>",
        unsafe_allow_html=True,
    )

    selected_seats = [
        seats_by_id[seat_id] for seat_id in selected_ids
        if seat_id in seats_by_id
    ]

    if st.session_state["booking_show_confirm_dialog"] and len(selected_seats) == required_count:
        _seat_confirmation_dialog(selected_seats, show_id)
