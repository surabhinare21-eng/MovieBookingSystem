import json
import os

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Booking Payment",
    page_icon="💳",
    layout="centered",
)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.title("💳 Booking Payment")
st.write("Complete your booking payment securely with Razorpay.")

# Obtain this token from your existing login flow.
# Do not ask users to paste their token into a public app.
access_token = st.session_state.get("access_token")

if not access_token:
    st.warning("Please log in before making a payment.")
    st.stop()

with st.form("booking_payment_form"):
    booking_id = st.number_input(
        "Booking ID",
        min_value=1,
        step=1,
        value=1,
    )

    create_order_clicked = st.form_submit_button(
        "Continue to payment",
        type="primary",
        use_container_width=True,
    )


if create_order_clicked:
    try:
        response = requests.post(
            f"{API_BASE_URL}/payments/create-order/{int(booking_id)}",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=20,
        )

        if response.status_code != 200:
            try:
                detail = response.json().get(
                    "detail",
                    "Unable to create payment order.",
                )
            except ValueError:
                detail = "Unable to create payment order."

            st.error(f"Payment order failed: {detail}")
            st.stop()

        order = response.json()

        # Store the server-created order for this Streamlit session.
        st.session_state["payment_order"] = order
        st.session_state["payment_booking_id"] = int(booking_id)

    except requests.RequestException:
        st.error(
            "Could not connect to the payment server. "
            "Check whether FastAPI is running."
        )
        st.stop()


order = st.session_state.get("payment_order")

if order:
    amount_rupees = order["amount"] / 100

    st.divider()
    st.subheader("Order summary")

    st.write(f"**Booking ID:** {order['booking_id']}")
    st.write(f"**Amount:** ₹{amount_rupees:,.2f}")
    st.write(f"**Status:** {order['payment_status']}")

    st.caption(
        "Your final payment status will be confirmed "
        "by the backend after verification."
    )

    # Serialize values safely before embedding them in JavaScript.
    key_id_js = json.dumps(order["razorpay_key_id"])
    order_id_js = json.dumps(order["razorpay_order_id"])
    amount_js = json.dumps(order["amount"])
    currency_js = json.dumps(order["currency"])
    api_url_js = json.dumps(API_BASE_URL)
    token_js = json.dumps(access_token)

    checkout_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
      <style>
        body {{
          font-family: sans-serif;
          margin: 0;
          padding: 12px 0;
        }}
        button {{
          width: 100%;
          padding: 14px;
          background: #1769ff;
          color: white;
          border: 0;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        }}
        button:disabled {{
          opacity: 0.6;
          cursor: wait;
        }}
        #result {{
          margin-top: 14px;
          overflow-wrap: anywhere;
          line-height: 1.5;
        }}
      </style>
    </head>
    <body>
      <button id="payButton" onclick="startPayment()">
        Pay ₹{amount_rupees:,.2f} with Razorpay
      </button>
      <div id="result" role="status"></div>

      <script>
        const keyId = {key_id_js};
        const orderId = {order_id_js};
        const amount = {amount_js};
        const currency = {currency_js};
        const apiBase = {api_url_js};
        const accessToken = {token_js};

        const result = document.getElementById("result");
        const payButton = document.getElementById("payButton");

        async function startPayment() {{
          if (typeof Razorpay === "undefined") {{
            result.textContent =
              "Razorpay Checkout could not load. Please refresh and retry.";
            return;
          }}

          payButton.disabled = true;
          result.textContent = "";

          const options = {{
            key: keyId,
            amount: amount,
            currency: currency,
            order_id: orderId,
            name: "Booking Payment",
            description: "Booking #" + {json.dumps(str(order["booking_id"]))},

            handler: async function (response) {{
              result.textContent = "Payment received. Verifying securely...";

              try {{
                const verification = await fetch(
                  apiBase + "/payments/verify",
                  {{
                    method: "POST",
                    headers: {{
                      "Content-Type": "application/json",
                      "Authorization": "Bearer " + accessToken
                    }},
                    body: JSON.stringify({{
                      razorpay_order_id: response.razorpay_order_id,
                      razorpay_payment_id: response.razorpay_payment_id,
                      razorpay_signature: response.razorpay_signature
                    }})
                  }}
                );

                const data = await verification.json();

                if (!verification.ok) {{
                  result.textContent =
                    "Verification is not confirmed: " +
                    (data.detail || "Please check your payment status.");
                  return;
                }}

                result.textContent =
                  "Payment verified successfully! Payment ID: " +
                  (data.razorpay_payment_id || response.razorpay_payment_id);

                payButton.textContent = "Payment successful";
              }} catch (error) {{
                result.textContent =
                  "We could not confirm the payment status. " +
                  "Please check your booking/payment status before retrying.";
              }} finally {{
                payButton.disabled = false;
              }}
            }},

            modal: {{
              ondismiss: function () {{
                result.textContent =
                  "Checkout closed. Your payment status has not been confirmed here.";
                payButton.disabled = false;
              }}
            }},

            theme: {{
              color: "#1769ff"
            }}
          }};

          const checkout = new Razorpay(options);

          checkout.on("payment.failed", function (response) {{
            const description =
              response.error && response.error.description
                ? response.error.description
                : "Please try again.";

            result.textContent = "Payment failed: " + description;
            payButton.disabled = false;
          }});

          checkout.open();
        }}
      </script>
    </body>
    </html>
    """

    components.html(
        checkout_html,
        height=210,
        scrolling=False,
    )