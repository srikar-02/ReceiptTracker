import streamlit as st
from google import genai
import re

st.set_page_config(
    page_title="Receipt Tracker",
    page_icon="🧾"
)

st.title("🧾 Receipt & Expense Tracker")
st.write("Upload a receipt and let AI extract the items and total.")

# Gemini client
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# Store receipt details
if "receipt_details" not in st.session_state:
    st.session_state.receipt_details = ""

# Store total amount
if "total_amount" not in st.session_state:
    st.session_state.total_amount = 0.0


# Upload receipt
uploaded_file = st.file_uploader(
    "Upload a receipt image",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded Receipt",
        use_container_width=True
    )

    if st.button("🔍 Analyze Receipt"):

        with st.spinner("Reading your receipt..."):

            image_bytes = uploaded_file.getvalue()

            prompt = """
            Analyze this receipt image.

            Extract:
            1. Each item name
            2. The price of each item
            3. The final total amount

            Return EXACTLY in this format:

            Items:
            - Item name: price
            - Item name: price

            Total: number

            Example:
            Total: 535.50

            Important:
            - Use the final amount the customer has to pay.
            - Do not use the subtotal if a final total is shown.
            - Do not include the ₹ symbol in the Total number.
            - Do not invent information.
            - If something cannot be read clearly, say "Not readable".
            """

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    {
                        "inline_data": {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes
                        }
                    },
                    prompt
                ]
            )

            result = response.text

            # Save receipt details
            st.session_state.receipt_details = result

            # Extract total automatically
            match = re.search(
                r"Total:\s*₹?\s*([0-9]+(?:\.[0-9]+)?)",
                result,
                re.IGNORECASE
            )

            if match:
                st.session_state.total_amount = float(match.group(1))
            else:
                st.session_state.total_amount = 0.0


# Display receipt details
if st.session_state.receipt_details:

    st.subheader("📋 Receipt Details")

    st.write(st.session_state.receipt_details)

    # Bill splitting
    st.subheader("👥 Split the Bill")

    people = st.number_input(
        "How many people?",
        min_value=1,
        value=1,
        step=1
    )

    if people >= 2:

        if st.button("💰 Calculate Split"):

            total = st.session_state.total_amount

            if total > 0:

                share = total / people

                st.success(f"Total Bill: ₹{total:.2f}")
                st.success(
                    f"Each Person Pays: ₹{share:.2f}"
                )

            else:
                st.error(
                    "Could not detect the total amount."
                )

    else:
        st.info(
            "👤 Bill splitting is only needed for 2 or more people."
        )