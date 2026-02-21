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

st.subheader("Transaction 1 – Dispense + Trigger Execution")
st.info("This will create a prescription, dispense medication, and reduce stock using triggers.")

col1, col2 = st.columns([1, 2])

with col1:
    run_tx = st.button("🚀 Run Transaction")

with col2:
    st.caption("Click to simulate dispensing medication for a high-urgency prescription.")

st.divider()

if run_tx:
    try:
        st.write("🔍 Checking inventory BEFORE transaction...")

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                # ---- CHECK BEFORE ----
                cur.execute("""
                    SELECT qty_on_hand 
                    FROM inventory_lot 
                    WHERE lot_batch_id = 3001;
                """)
                before_qty = cur.fetchone()[0]

                # ---- START TRANSACTION ----
                cur.execute("BEGIN;")

                # 1. Insert Prescription
                cur.execute("""
                    INSERT INTO prescription 
                    (rx_id, rx_date, status, urgency, patient_id, doctor_id, pharmacist_id)
                    VALUES (4101, CURRENT_DATE, 'Dispensed', 'High', 601, 701, 801);
                """)

                # 2. Insert Prescription Item
                cur.execute("""
                    INSERT INTO prescription_items
                    (rx_id, drug_id, qty_prescribed, dosage_instruc, frequency, refills_allowed)
                    VALUES (4101, 2001, 5, 'Take with water', '2x daily', 0);
                """)

                # 3. Create Dispense Record
                cur.execute("""
                    INSERT INTO dispense
                    (dispense_id, dispense_date, total_amount, commission, pharmacist_id, rx_id)
                    VALUES (5101, CURRENT_DATE, 12.00, 1.20, 801, 4101);
                """)

                # 4. This fires triggers (stock reduction)
                cur.execute("""
                    INSERT INTO dispensed_items
                    (line_item_id, qty_dispensed, dispense_id, lot_batch_id)
                    VALUES (6101, 2, 5101, 3001);
                """)

                # ---- COMMIT ----
                conn.commit()

                # ---- CHECK AFTER ----
                cur.execute("""
                    SELECT qty_on_hand 
                    FROM inventory_lot 
                    WHERE lot_batch_id = 3001;
                """)
                after_qty = cur.fetchone()[0]

        # ---- DISPLAY RESULTS ----
        st.success("✅ Transaction completed successfully!")
        st.balloons()

        colA, colB = st.columns(2)
        with colA:
            st.metric("Inventory Before", before_qty)
        with colB:
            st.metric("Inventory After", after_qty)

    except Exception as e:
        st.error("❌ Transaction failed. Rolling back...")
        st.write(str(e))