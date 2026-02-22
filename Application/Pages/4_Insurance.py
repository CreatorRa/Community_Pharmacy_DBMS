import streamlit as st
import pandas as pd
import datetime as dt
from db import get_connection

# =====================================================================
# Page setup
# =====================================================================
st.set_page_config(page_title="Dispense Medication", layout="wide")
st.title("Dispense Management")
st.markdown("Dispense medication safely and manage reversals. Inventory safety checks are enforced by database triggers.")
st.divider()

tab1, tab2 = st.tabs(["Dispense Medication", "Reverse Dispense"])

# =====================================================================
# Helpers
# =====================================================================
@st.cache_data(ttl=60)
def load_dropdowns():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT pharmacist_id, name FROM pharmacist ORDER BY pharmacist_id;")
        pharmacists = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

        cur.execute("SELECT patient_id, name FROM patient ORDER BY patient_id;")
        patients = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

        cur.execute("SELECT doctor_id, name FROM doctor ORDER BY doctor_id;")
        doctors = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

        cur.execute("SELECT drug_id, drug_name FROM drug_catalogue ORDER BY drug_id;")
        drugs = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    return pharmacists, patients, doctors, drugs


def next_id(table_name: str, id_col: str) -> int:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(MAX({id_col}), 0) + 1 FROM {table_name};")
        return int(cur.fetchone()[0])


def lots_for_drug(drug_id: int) -> pd.DataFrame:
    conn = get_connection()
    q = """
        SELECT
            lot_batch_id,
            qty_on_hand,
            unit_cost,
            expiry_date
        FROM inventory_lot
        WHERE drug_id = %s
        ORDER BY expiry_date ASC, qty_on_hand DESC;
    """
    df = pd.read_sql(q, conn, params=(drug_id,))
    if not df.empty:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date
    return df


# =====================================================================
# TAB 1: DISPENSE (implements your Tx1)
# =====================================================================
with tab1:
    st.subheader("Dispense Medication")
    st.caption("Creates a prescription + dispense record and dispenses one item from a selected lot. Inventory and expiry rules are enforced by DB triggers.")

    pharmacists, patients, doctors, drugs = load_dropdowns()

    c1, c2, c3 = st.columns(3)
    with c1:
        default_rx = next_id("prescription", "rx_id")
        rx_id = st.number_input("Prescription ID", min_value=1, value=default_rx, step=1)
    with c2:
        default_dispense = next_id("dispense", "dispense_id")
        dispense_id = st.number_input("Dispense ID", min_value=1, value=default_dispense, step=1)
    with c3:
        default_line = next_id("dispensed_items", "line_item_id")
        line_item_id = st.number_input("Dispensed Item Line ID", min_value=1, value=default_line, step=1)

    with st.form("dispense_form"):
        left, right = st.columns(2)

        with left:
            pharmacist_sel = st.selectbox("Pharmacist", pharmacists)
            patient_sel = st.selectbox("Patient", patients)
            doctor_sel = st.selectbox("Doctor", doctors)

            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"], index=2)

        with right:
            drug_sel = st.selectbox("Drug", drugs)
            qty_prescribed = st.number_input("Quantity prescribed", min_value=1, value=5, step=1)
            qty_dispensed = st.number_input("Quantity to dispense now", min_value=1, value=2, step=1)

            dosage = st.text_input("Dosage instructions", value="Take with water")
            frequency = st.text_input("Frequency", value="2x daily")
            refills_allowed = st.number_input("Refills allowed", min_value=0, value=0, step=1)

        submitted = st.form_submit_button("Dispense Now", type="primary")

    # After submit: show lots + execute
    if submitted:
        pharmacist_id = int(pharmacist_sel.split(" - ")[0])
        patient_id = int(patient_sel.split(" - ")[0])
        doctor_id = int(doctor_sel.split(" - ")[0])
        drug_id = int(drug_sel.split(" - ")[0])

        lots_df = lots_for_drug(drug_id)

        if lots_df.empty:
            st.error("No inventory lots exist for this drug. Please add inventory first.")
            st.stop()

        # Filter to lots that are not expired (DB will still block expired, but this helps UX)
        lots_df_valid = lots_df[lots_df["expiry_date"] >= dt.date.today()].copy()
        if lots_df_valid.empty:
            st.error("All lots for this drug are expired. Dispensing is not possible.")
            st.stop()

        # Build dropdown options from DataFrame columns (avoid attribute errors)
        lot_options = [
            f"{int(row['lot_batch_id'])} | on-hand: {int(row['qty_on_hand'])} | unit_cost: {float(row['unit_cost']):.2f} | exp: {row['expiry_date']}"
            for _, row in lots_df_valid.iterrows()
        ]

        st.markdown("### Select inventory lot for dispensing")
        selected_lot = st.selectbox("Lot batch", lot_options)
        lot_batch_id = int(selected_lot.split("|")[0].strip())

        # Pull the chosen lot details
        chosen = lots_df_valid[lots_df_valid["lot_batch_id"] == lot_batch_id].iloc[0]
        unit_cost = float(chosen["unit_cost"])
        on_hand = int(chosen["qty_on_hand"])

        est_total = qty_dispensed * unit_cost
        est_commission = round(est_total * 0.05, 2)  # 5%

        st.info(
            f"Estimated total: €{est_total:.2f} (qty {qty_dispensed} × unit_cost €{unit_cost:.2f}). "
            f"Commission (5%): €{est_commission:.2f}. Current on-hand: {on_hand}."
        )

        if st.button("Confirm & Save Dispense", type="primary", use_container_width=True):
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("BEGIN;")

                    # 1) Prescription (we set status to Dispensed to reflect the completed action)
                    cur.execute(
                        """
                        INSERT INTO prescription (rx_id, rx_date, status, urgency, patient_id, doctor_id, pharmacist_id)
                        VALUES (%s, CURRENT_DATE, 'Dispensed', %s, %s, %s, %s);
                        """,
                        (rx_id, urgency, patient_id, doctor_id, pharmacist_id),
                    )

                    # 2) Prescription item (composite PK: rx_id, drug_id)
                    cur.execute(
                        """
                        INSERT INTO prescription_items (rx_id, drug_id, qty_prescribed, dosage_instruc, frequency, refills_allowed)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (rx_id, drug_id, qty_prescribed, dosage, frequency, refills_allowed),
                    )

                    # 3) Dispense record (total + commission stored)
                    cur.execute(
                        """
                        INSERT INTO dispense (dispense_id, dispense_date, total_amount, commission, pharmacist_id, rx_id)
                        VALUES (%s, CURRENT_DATE, %s, %s, %s, %s);
                        """,
                        (dispense_id, est_total, est_commission, pharmacist_id, rx_id),
                    )

                    # 4) Dispensed item (DB triggers run here: expiry check, stock check, reduce stock)
                    cur.execute(
                        """
                        INSERT INTO dispensed_items (line_item_id, qty_dispensed, dispense_id, lot_batch_id)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (line_item_id, qty_dispensed, dispense_id, lot_batch_id),
                    )

                    conn.commit()

                st.success("Dispense saved successfully.")

                # Receipt (live JOINs)
                receipt_q = """
                    SELECT
                        di.line_item_id      AS "Line",
                        dp.dispense_id       AS "Dispense ID",
                        dp.dispense_date     AS "Date",
                        p.name               AS "Patient",
                        ph.name              AS "Pharmacist",
                        dc.drug_name         AS "Drug",
                        di.qty_dispensed     AS "Qty dispensed",
                        il.unit_cost         AS "Unit cost",
                        dp.total_amount      AS "Total amount",
                        dp.commission        AS "Commission",
                        il.lot_batch_id      AS "Lot batch",
                        il.expiry_date       AS "Expiry"
                    FROM dispensed_items di
                    JOIN dispense dp        ON di.dispense_id = dp.dispense_id
                    JOIN prescription rx    ON dp.rx_id = rx.rx_id
                    JOIN patient p          ON rx.patient_id = p.patient_id
                    JOIN pharmacist ph      ON dp.pharmacist_id = ph.pharmacist_id
                    JOIN inventory_lot il   ON di.lot_batch_id = il.lot_batch_id
                    JOIN drug_catalogue dc  ON il.drug_id = dc.drug_id
                    WHERE dp.dispense_id = %s
                    ORDER BY di.line_item_id;
                """
                df_receipt = pd.read_sql(receipt_q, get_connection(), params=(dispense_id,))
                st.markdown("### Dispense Receipt (Database Proof)")
                st.dataframe(df_receipt, use_container_width=True, hide_index=True)

                inv_q = "SELECT lot_batch_id, qty_on_hand FROM inventory_lot WHERE lot_batch_id = %s;"
                df_inv = pd.read_sql(inv_q, get_connection(), params=(lot_batch_id,))
                st.caption("Inventory check after dispensing:")
                st.dataframe(df_inv, use_container_width=True, hide_index=True)

            except Exception as e:
                conn.rollback()
                st.error(f"Dispense failed and was rolled back.\n\nError: {e}")


# =====================================================================
# TAB 2: REVERSE DISPENSE (implements your Tx2)
# =====================================================================
with tab2:
    st.subheader("Reverse a Dispense")
    st.caption("Safely reverses a dispense by restoring inventory first, then deleting child → parent records.")

    conn = get_connection()
    dispenses_df = pd.read_sql(
        """
        SELECT dispense_id, dispense_date, total_amount, rx_id
        FROM dispense
        ORDER BY dispense_id DESC
        LIMIT 50;
        """,
        conn,
    )

    if dispenses_df.empty:
        st.info("No dispense records found yet.")
    else:
        # Build selection safely from DataFrame column names (avoid itertuples attribute mismatch)
        dispenses_df["label"] = dispenses_df.apply(
            lambda r: f"{int(r['dispense_id'])} | {r['dispense_date']} | total: €{float(r['total_amount']):.2f} | rx: {int(r['rx_id'])}",
            axis=1,
        )
        selected = st.selectbox("Select a dispense to reverse", dispenses_df["label"].tolist())
        selected_dispense_id = int(selected.split("|")[0].strip())

        # Preview what will be reversed
        preview_q = """
            SELECT
                di.line_item_id,
                di.qty_dispensed,
                di.lot_batch_id,
                il.qty_on_hand AS qty_on_hand_before
            FROM dispensed_items di
            JOIN inventory_lot il ON di.lot_batch_id = il.lot_batch_id
            WHERE di.dispense_id = %s
            ORDER BY di.line_item_id;
        """
        preview_df = pd.read_sql(preview_q, get_connection(), params=(selected_dispense_id,))
        st.markdown("### Items in this dispense")
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

        if st.button("Reverse this dispense", type="primary", use_container_width=True):
            conn2 = get_connection()
            try:
                with conn2.cursor() as cur:
                    cur.execute("BEGIN;")

                    # Fetch rx_id for the selected dispense
                    cur.execute("SELECT rx_id FROM dispense WHERE dispense_id = %s;", (selected_dispense_id,))
                    row = cur.fetchone()
                    if not row:
                        raise Exception("Selected dispense no longer exists.")
                    rx_id_to_delete = int(row[0])

                    # 1) Restore inventory for each dispensed line
                    cur.execute(
                        "SELECT lot_batch_id, qty_dispensed FROM dispensed_items WHERE dispense_id = %s;",
                        (selected_dispense_id,),
                    )
                    rows = cur.fetchall()
                    for lot_id, qty in rows:
                        cur.execute(
                            """
                            UPDATE inventory_lot
                            SET qty_on_hand = qty_on_hand + %s
                            WHERE lot_batch_id = %s;
                            """,
                            (qty, lot_id),
                        )

                    # 2) Delete child → parent
                    cur.execute("DELETE FROM dispensed_items WHERE dispense_id = %s;", (selected_dispense_id,))
                    cur.execute("DELETE FROM dispense WHERE dispense_id = %s;", (selected_dispense_id,))
                    cur.execute("DELETE FROM prescription_items WHERE rx_id = %s;", (rx_id_to_delete,))
                    cur.execute("DELETE FROM prescription WHERE rx_id = %s;", (rx_id_to_delete,))

                    conn2.commit()

                st.success("Dispense reversed successfully. Inventory restored and records removed.")

                # Verification: show the (now missing) dispense and updated inventory
                verify_disp = pd.read_sql(
                    "SELECT * FROM dispense WHERE dispense_id = %s;",
                    get_connection(),
                    params=(selected_dispense_id,),
                )
                st.caption("Verification: dispense should be gone (empty table below):")
                st.dataframe(verify_disp, use_container_width=True, hide_index=True)

                if not preview_df.empty:
                    lot_ids = preview_df["lot_batch_id"].tolist()
                    inv_after = pd.read_sql(
                        f"SELECT lot_batch_id, qty_on_hand FROM inventory_lot WHERE lot_batch_id = ANY(%s) ORDER BY lot_batch_id;",
                        get_connection(),
                        params=(lot_ids,),
                    )
                    st.caption("Inventory after reversal:")
                    st.dataframe(inv_after, use_container_width=True, hide_index=True)

            except Exception as e:
                conn2.rollback()
                st.error(f"Reversal failed and was rolled back.\n\nError: {e}")
