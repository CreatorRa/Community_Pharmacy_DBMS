import streamlit as st
import pandas as pd
from db import get_connection

st.set_page_config(page_title="Insurance Coverage", layout="wide")
st.title("Insurance Coverage")
st.markdown("Record insurance payments for completed dispenses, and undo mistakes safely.")
st.divider()

# ==========================================================
# Load Dispenses & Insurance Policies
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
# Select Dispense
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

# ==========================================================
# Select Insurance Policy
# ==========================================================
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
# Check Existing Coverage
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
    f"Total Dispense: €{selected_total:.2f}\n\n"
    f"Already Covered: €{already_covered:.2f}\n\n"
    f"Remaining Balance: €{remaining_balance:.2f}"
)

# ==========================================================
# Tabs: Add Coverage / Rollback
# ==========================================================
tab_add, tab_rollback = st.tabs(["Add Insurance Coverage", "Rollback / Undo"])

# ==========================================================
# TAB 1 — Add Insurance Coverage (INSERT into PAYS)
# ==========================================================
with tab_add:
    if remaining_balance <= 0:
        st.success("This dispense is already fully covered.")
    else:
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

                    if amount <= 0:
                        raise Exception("Amount must be greater than 0.")
                    if amount > remaining_balance:
                        raise Exception("Amount exceeds remaining balance.")

                    cur.execute("""
                        INSERT INTO pays (dispense_id, policy_id, amount_covered)
                        VALUES (%s, %s, %s);
                    """, (selected_dispense_id, selected_policy_id, amount))

                    cur.execute("COMMIT;")

                st.success("Insurance coverage recorded successfully.")
                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"Failed to record insurance coverage.\n\nError: {e}")

# ==========================================================
# TAB 2 — Rollback / Undo (DELETE from PAYS)
# ==========================================================
with tab_rollback:
    st.subheader("Undo an Insurance Payment")
    st.caption("Use this if an insurance payment was entered incorrectly. This will delete a PAYS row inside a transaction.")

    pays_rows = pd.read_sql("""
        SELECT
            p.dispense_id,
            p.policy_id,
            i.company,
            p.amount_covered
        FROM pays p
        JOIN insurance i ON p.policy_id = i.policy_id
        WHERE p.dispense_id = %s
        ORDER BY p.policy_id;
    """, get_connection(), params=(selected_dispense_id,))

    if pays_rows.empty:
        st.info("No insurance payments found for this dispense. Nothing to rollback.")
    else:
        # Build selectable labels (composite PK: dispense_id + policy_id)
        pays_rows["label"] = pays_rows.apply(
            lambda r: f"Policy {int(r['policy_id'])} - {r['company']} | Covered: €{float(r['amount_covered']):.2f}",
            axis=1
        )

        selected_payment_label = st.selectbox(
            "Select the insurance payment to undo",
            pays_rows["label"].tolist()
        )

        # Get policy_id from selection
        selected_row = pays_rows[pays_rows["label"] == selected_payment_label].iloc[0]
        rollback_policy_id = int(selected_row["policy_id"])

        st.warning(
            "This action deletes the selected insurance record from PAYS.\n"
            "It does NOT delete the dispense itself."
        )

        confirm = st.checkbox("I confirm I want to undo this insurance payment.")

        if st.button("Undo Selected Payment", type="primary", disabled=not confirm):
            try:
                rb_conn = get_connection()
                with rb_conn.cursor() as cur:
                    cur.execute("BEGIN;")

                    # Delete the exact row using the composite PK
                    cur.execute("""
                        DELETE FROM pays
                        WHERE dispense_id = %s AND policy_id = %s;
                    """, (selected_dispense_id, rollback_policy_id))

                    # Safety: ensure something was deleted
                    if cur.rowcount != 1:
                        raise Exception("Rollback failed: record not found or multiple rows affected.")

                    cur.execute("COMMIT;")

                st.success("Insurance payment undone successfully.")
                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                try:
                    rb_conn.rollback()
                except Exception:
                    pass
                st.error(f"Rollback failed.\n\nError: {e}")

    st.divider()
    st.markdown("### Current Insurance Records (Verification)")
    verification_df = pd.read_sql("""
        SELECT p.dispense_id,
               i.company,
               p.amount_covered
        FROM pays p
        JOIN insurance i ON p.policy_id = i.policy_id
        WHERE p.dispense_id = %s
        ORDER BY i.company;
    """, get_connection(), params=(selected_dispense_id,))
    st.dataframe(verification_df, use_container_width=True, hide_index=True)
