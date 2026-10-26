import streamlit as st

from common import api


def my_bookings_page() -> None:
    st.title("My Bookings")
    st.caption("Your movie tickets and payment details.")

    ok, bookings, code = api("GET", "/payments/my-bookings")
    if not ok:
        st.error(f"Could not load your bookings (HTTP {code}): {bookings}")
        return

    if not bookings:
        st.info("No Booking has been done by You")
        if st.button("GO TO HOME PAGE", type="primary"):
            st.session_state["customer_view"] = "home"
            st.session_state["booking_step"] = "cities"
            st.rerun()
        return

    for booking in bookings:
        with st.container(border=True):
            st.subheader(booking.get("movie_name", "Movie"))
            st.write(f"**Booking ID:** {booking.get('booking_id')}")
            st.write(f"**Theatre Name:** {booking.get('theatre_name', 'Theatre')}")
            st.write(f"**Screen Name:** {booking.get('screen_name', 'Screen')}")
            st.write(f"**Seats Booked:** {', '.join(booking.get('seat_labels') or []) or 'Not available'}")
            st.write(f"**Total Amount Paid:** ₹{booking.get('amount', '0.00')}")
            st.write(f"**Paid at:** {booking.get('paid_at') or 'Not paid'}")
            st.write(f"**Payment Type:** {booking.get('payment_type') or 'Not available'}")
            st.write(f"**Transaction ID:** {booking.get('transaction_id') or 'Not available'}")
            if booking.get("payment_status") == "SUCCESS":
                st.success("Enjoy your show! 🍿")
            else:
                st.warning(f"Payment status: {booking.get('payment_status', 'PENDING')}")

    st.divider()
    return_booking_id = st.session_state.get("my_bookings_return_to_payment")
    col1, col2 = st.columns(2)
    with col1:
        if return_booking_id and st.button("BACK TO PAYMENT SUCCESSFUL PAGE", type="primary", use_container_width=True):
            st.session_state["payment_booking_id"] = return_booking_id
            st.session_state["customer_view"] = "home"
            st.session_state["booking_step"] = "payment"
            st.rerun()
    with col2:
        if st.button("RETURN TO HOME PAGE", use_container_width=True):
            st.session_state["customer_view"] = "home"
            st.session_state["booking_step"] = "cities"
            st.rerun()
