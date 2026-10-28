import json

import streamlit as st
import streamlit.components.v1 as components

from common import api

st.set_page_config(page_title="Booking Payment", page_icon="💳", layout="centered")

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

CHECKOUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
  <style>
    body { font-family: -apple-system, "Segoe UI", Arial, sans-serif; margin: 0; padding: 4px 0; }
    button {
      width: 100%; padding: 14px; border: 0; border-radius: 8px;
      background: #111827; color: #fff; font-size: 16px; font-weight: 600; cursor: pointer;
    }
    button:hover:not(:disabled) { background: #263449; }
    button:disabled { opacity: .6; cursor: not-allowed; }
    #msg { margin-top: 12px; font-size: 14px; line-height: 1.5; color: #374151; }
    #msg.ok { color: #15803d; }
    #msg.err { color: #b91c1c; }
  </style>
</head>
<body>
  <button id="pay"></button>
  <div id="msg" role="status"></div>

  <script>
    const cfg = __CONFIG__;
    const btn = document.getElementById("pay");
    const msg = document.getElementById("msg");
    const label = "Pay " + new Intl.NumberFormat("en-IN", {
      style: "currency", currency: cfg.currency
    }).format(cfg.amount / 100);

    btn.textContent = label;
    btn.style.display = "none";
    btn.onclick = startPayment;
    window.addEventListener("load", startPayment);

    function showButton() {
      btn.textContent = "Reopen payment";
      btn.style.display = "block";
      btn.disabled = false;
    }

    function show(text, kind) {
      msg.textContent = text;
      msg.className = kind || "";
    }

    async function verify(res) {
      show("Verifying payment...");
      try {
        const r = await fetch(cfg.apiBase + "/payments/verify", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + cfg.token
          },
          body: JSON.stringify({
            razorpay_order_id: res.razorpay_order_id,
            razorpay_payment_id: res.razorpay_payment_id,
            razorpay_signature: res.razorpay_signature
          })
        });
        const data = await r.json().catch(() => ({}));
        if (!r.ok) {
          show(data.detail || "Verification failed. Please check your booking status.", "err");
          showButton();
          return;
        }
        show("Payment successful! Return to the booking page and click Check payment status to see your ticket details.", "ok");
      } catch (e) {
        show("Could not confirm payment. Check your booking status before retrying.", "err");
        showButton();
      }
    }

    function startPayment() {
      if (typeof Razorpay === "undefined") {
        show("Checkout failed to load. Please refresh and try again.", "err");
        return;
      }
      btn.style.display = "none";
      show("");

      const rzp = new Razorpay({
        key: cfg.keyId,
        order_id: cfg.orderId,
        amount: cfg.amount,
        currency: cfg.currency,
        name: "Booking Payment",
        description: "Booking #" + cfg.bookingId,
        theme: { color: "#111827" },
        handler: verify,
        modal: {
          ondismiss: function () {
            show("Checkout closed. No payment was made.");
            showButton();
          }
        }
      });

      rzp.on("payment.failed", function (r) {
        show("Payment failed: " + ((r.error && r.error.description) || "Please try again."), "err");
        showButton();
      });

      rzp.open();
    }
  </script>
</body>
</html>
"""


def render_checkout(order: dict, token: str) -> None:
    """Render the Razorpay Checkout button inside an iframe."""
    config = {
        "keyId": order["razorpay_key_id"],
        "orderId": order["razorpay_order_id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "bookingId": str(order["booking_id"]),
        "apiBase": st.session_state.get("backend_url", DEFAULT_BACKEND_URL).rstrip("/"),
        "token": token,
    }
    config_js = json.dumps(config).replace("</", "<\\/")
    # Razorpay's modal renders inside this iframe, so it needs enough height.
    components.html(CHECKOUT_TEMPLATE.replace("__CONFIG__", config_js), height=720)


HIDE_CHROME = """
<style>
  header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] { display: none !important; }
  .block-container { padding-top: 0 !important; }
</style>
"""


def _return_home() -> None:
    for key in (
        "payment_order", "payment_booking_id", "booking_lock_seats",
        "booking_show_id", "booking_seat_ids", "booking_total_amount",
    ):
        st.session_state.pop(key, None)
    st.session_state["booking_step"] = "cities"
    st.rerun()


def _return_to_seats() -> None:
    st.session_state.pop("payment_order", None)
    st.session_state.pop("payment_booking_id", None)
    st.session_state["booking_step"] = "seats"
    st.rerun()


def _show_success(details: dict, booking_id: int) -> None:
    st.markdown(
        "<div style='text-align:center;padding:24px 12px 12px'>"
        "<div style='font-size:64px;line-height:1.1'>✅</div>"
        "<h1 style='color:#15803d;font-size:42px;margin:12px 0'>"
        "Your Payment is Successful!</h1></div>",
        unsafe_allow_html=True,
    )
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Total amount paid", f"₹{details.get('amount', '0.00')}")
    col2.metric("Payment Type", details.get("payment_type") or "RAZORPAY")
    st.write(f"**Paid at:** {details.get('paid_at') or 'Not available'}")
    st.write(f"**Transaction ID:** {details.get('transaction_id') or 'Not available'}")
    st.write(f"**Booking ID:** {booking_id}")
    st.divider()
    if st.button("VIEW YOUR BOOKINGS", type="primary", use_container_width=True):
        st.session_state["customer_view"] = "my_bookings"
        st.session_state["my_bookings_return_to_payment"] = booking_id
        st.rerun()
    if st.button("RETURN TO HOME PAGE", use_container_width=True):
        _return_home()

@st.fragment(run_every="2s")
def watch_payment_status(booking_id: int):
    """Automatically detect successful payment and display confirmation."""
    ok, details, status_code = api(
        "GET",
        f"/payments/booking/{booking_id}"
    )

    if ok and details.get("payment_status") == "SUCCESS":
        st.rerun()

    st.caption("Waiting for payment confirmation...")

def payments_page() -> None:
    token = st.session_state.get("token")
    if not token:
        st.warning("Please log in before making a payment.")
        st.stop()

    booking_id = st.session_state.get("payment_booking_id")
    locks = st.session_state.get("booking_lock_seats", [])
    if booking_id is None and locks:
        booking_id = locks[0].get("booking_id")
    if booking_id is None:
        st.error("Your seat hold has expired or is missing. Please select seats again.")
        if st.button("BACK TO SEAT SELECTION", type="primary"):
            _return_to_seats()
        return

    ok, details, status_code = api("GET", f"/payments/booking/{booking_id}")
    if ok and details.get("payment_status") == "SUCCESS":
        _show_success(details, booking_id)
        return

    order = st.session_state.get("payment_order")
    st.title("💳 Booking Payment")
    st.caption("Secure checkout powered by Razorpay.")

    if order is None:
        st.info("Your selected seats are held for 5 minutes.")
        if st.button("Continue to payment", type="primary", use_container_width=True):
            ok, response, code = api("POST", f"/payments/create-order/{booking_id}")
            if not ok:
                st.error(f"Could not create payment order (HTTP {code}): {response}")
                return
            st.session_state["payment_order"] = response
            st.session_state["payment_booking_id"] = booking_id
            st.rerun()
        if st.button("BACK TO SEAT SELECTION", use_container_width=True):
            _return_to_seats()
        return

    render_checkout(order, token)
    watch_payment_status(booking_id)
