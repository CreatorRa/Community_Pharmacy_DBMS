import streamlit as st
import pandas as pd
from db import get_connection

st.set_page_config(page_title="Insurance Coverage", layout="wide")
st.title("Insurance Coverage Management")
st.markdown("Record insurance payments for completed dispenses.")
st.divider()

# ==========================================================
# Load dropdown data
# ==========================================================
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()

    dispenses = pd.read_sql("""
        SELECT dispense_id, total_amount
        FROM dispense
        ORDER BY dispense_id DESC;
    """, conn)

    insurance = pd.read_sql("""
        SELECT policy_id, company
        FROM insurance
        ORDER BY policy_id;
    """, conn)

    return dispenses, insurance


dispenses_df, insurance_df = load_data()

if dispenses_df.empty:
    st.info("No dispenses found. Insurance can only be applied to existing dispenses.")
    st.stop()

# ==========================================================
# Selection Section
# ==========================================================
dispenses_df["label"] = dispenses_df.apply(
    lambda r: f"{int(r['dispense_id'])} | Total: €{float(r['total_amount']):.2f}",
    axis=1
)

selected_dispense_label = st.selectbox(
    "Select Dispense",
    dispenses_df["label"].tolist()
)

selected_dispense_id = int(selected_dispense_label.split("|")[0].strip())

selected_total = float(
    dispenses_df[dispenses_df["dispense_id"] == selected_dispense_id]["total_amount"].values[0]
)

insurance_df["label"] = insurance_df.apply(
    lambda r: f"{int(r['policy_id'])} - {r['company']}",
    axis=1
)

selected_policy_label = st.selectbox(
    "Select Insurance Company",
    insurance_df["label"].tolist()
)

selected_policy_id = int(selected_policy_label.split(" - ")[0])

# ==========================================================
# Check already covered amount
# ==========================================================
conn = get_connection()

covered_df = pd.read_sql("""
    SELECT COALESCE(SUM(amount_covered),0) AS covered
    FROM pays
    WHERE dispense_id = %s;
""", conn, params=(selected_dispense_id,))

already_covered = float(covered_df["covered"].values[0])
remaining_balance = round(selected_total - already_covered, 2)

st.info(
    f"Total Dispense: €{selected_total:.2f}  \n"
    f"Already Covered: €{already_covered:.2f}  \n"
    f"Remaining Balance: €{remaining_balance:.2f}"
)

if remaining_balance <= 0:
    st.success("This dispense is already fully covered.")
    st.stop()

# ==========================================================
# Coverage Form
# ==========================================================
with st.form("insurance_form"):
    amount = st.number_input(
        "Amount Covered by Insurance",
        min_value=0.0,
        max_value=remaining_balance,
        value=remaining_balance,
        step=1.0
    )

    submitted = st.form_submit_button("Record Insurance Payment", type="primary")

if submitted:
    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")

            # Prevent over-coverage
            if amount > remaining_balance:
                raise Exception("Amount exceeds remaining balance.")

            cur.execute("""
                INSERT INTO pays (dispense_id, policy_id, amount_covered)
                VALUES (%s, %s, %s);
            """, (selected_dispense_id, selected_policy_id, amount))

            conn.commit()

        st.success("Insurance coverage recorded successfully.")

        # Verification Table
        verification_df = pd.read_sql("""
            SELECT p.dispense_id,
                   i.company,
                   p.amount_covered
            FROM pays p
            JOIN insurance i ON p.policy_id = i.policy_id
            WHERE p.dispense_id = %s;
        """, get_connection(), params=(selected_dispense_id,))

        st.markdown("### Insurance Records for This Dispense")
        st.dataframe(verification_df, use_container_width=True, hide_index=True)

    except Exception as e:
        conn.rollback()
        st.error(f"Failed to record insurance coverage.\n\nError: {e}")
