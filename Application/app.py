import streamlit as st
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="Dispense | Pharmacy OS", page_icon="💊")

st.title("💊 Dispense Medication")
st.markdown("Process a prescription and automatically update inventory.")
st.divider()

LOT_ID = 3001
RX_ID = 4101
DISPENSE_ID = 5101
LINE_ITEM_ID = 6101

def get_qty(conn, lot_id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT qty_on_hand FROM inventory_lot WHERE lot_batch_id = %s;",
            (lot_id,),
        )
        row = cur.fetchone()
        return row[0] if row else None

# =========================
# Transaction 1
# =========================
st.subheader("Transaction 1 – Dispense + Trigger Execution")
st.info("Creates prescription + dispense and reduces stock using triggers.")

col1, col2 = st.columns([1, 2])
with col1:
    run_tx1 = st.button("🚀 Run Transaction 1")
with col2:
    st.caption("Simulates dispensing medication for a high-urgency prescription.")

if run_tx1:
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            before_qty = get_qty(conn, LOT_ID)

            with conn.cursor() as cur:
                cur.execute("BEGIN;")

                cur.execute("""
                    INSERT INTO prescription
                    (rx_id, rx_date, status, urgency, patient_id, doctor_id, pharmacist_id)
                    VALUES (%s, CURRENT_DATE, 'Dispensed', 'High', 601, 701, 801);
                """, (RX_ID,))

                cur.execute("""
                    INSERT INTO prescription_items
                    (rx_id, drug_id, qty_prescribed, dosage_instruc, frequency, refills_allowed)
                    VALUES (%s, 2001, 5, 'Take with water', '2x daily', 0);
                """, (RX_ID,))

                cur.execute("""
                    INSERT INTO dispense
                    (dispense_id, dispense_date, total_amount, commission, pharmacist_id, rx_id)
                    VALUES (%s, CURRENT_DATE, 12.00, 1.20, 801, %s);
                """, (DISPENSE_ID, RX_ID))

                # This insert fires triggers and reduces inventory stock
                cur.execute("""
                    INSERT INTO dispensed_items
                    (line_item_id, qty_dispensed, dispense_id, lot_batch_id)
                    VALUES (%s, 2, %s, %s);
                """, (LINE_ITEM_ID, DISPENSE_ID, LOT_ID))

                conn.commit()

            after_qty = get_qty(conn, LOT_ID)

        st.success("✅ Transaction 1 completed successfully!")
        cA, cB = st.columns(2)
        with cA:
            st.metric("Inventory Before", before_qty)
        with cB:
            st.metric("Inventory After", after_qty)

    except Exception as e:
        st.error("❌ Transaction 1 failed. Rolling back...")
        st.write(str(e))

st.divider()

# =========================
# Transaction 2
# =========================
st.subheader("Transaction 2 – Safe Reversal (Undo Transaction 1)")
st.warning("Restores inventory first, then deletes child → parent records safely.")

col3, col4 = st.columns([1, 2])
with col3:
    run_tx2 = st.button("↩️ Run Transaction 2 (Undo)")
with col4:
    st.caption("Use this if you want to reset the database and run Transaction 1 again.")

if run_tx2:
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            before_qty = get_qty(conn, LOT_ID)

            with conn.cursor() as cur:
                cur.execute("BEGIN;")

                # 1) Restore inventory FIRST (safe)
                cur.execute("""
                    UPDATE inventory_lot
                    SET qty_on_hand = qty_on_hand + 2
                    WHERE lot_batch_id = %s;
                """, (LOT_ID,))

                # 2) Delete from child to parent (safe)
                cur.execute("DELETE FROM dispensed_items WHERE line_item_id = %s;", (LINE_ITEM_ID,))
                cur.execute("DELETE FROM dispense WHERE dispense_id = %s;", (DISPENSE_ID,))
                cur.execute("DELETE FROM prescription_items WHERE rx_id = %s;", (RX_ID,))
                cur.execute("DELETE FROM prescription WHERE rx_id = %s;", (RX_ID,))

                conn.commit()

            after_qty = get_qty(conn, LOT_ID)

        st.success("✅ Transaction 2 completed successfully! (Undo done)")
        cC, cD = st.columns(2)
        with cC:
            st.metric("Inventory Before Undo", before_qty)
        with cD:
            st.metric("Inventory After Undo", after_qty)

    except Exception as e:
        st.error("❌ Transaction 2 failed. Rolling back...")
        st.write(str(e))