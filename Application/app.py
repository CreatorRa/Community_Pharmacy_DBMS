import streamlit as st
from db import get_connection, run_query

# 1. PAGE CONFIGURATION (Must be first)
st.set_page_config(
    page_title="Pharmacy OS | Home", 
    page_icon="⚕️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. HEADER SECTION
st.title("⚕️ Pharmacy Management System")
st.markdown("### Welcome to the Central Command Dashboard")
st.markdown("Use this portal to monitor inventory levels, manage patient prescriptions, and track supplier orders in real-time.")
st.divider()

# 3. LIVE SYSTEM METRICS (KPIs)
st.subheader("📊 Quick System Stats")

try:
    # We query the database for live stats to make the home page actually useful!
    patients_df = run_query("SELECT COUNT(*) FROM PATIENT;")
    low_stock_df = run_query("SELECT COUNT(*) FROM INVENTORY_LOT WHERE Qty_on_hand < 100;")
    pending_orders_df = run_query("SELECT COUNT(*) FROM PURCHASE_ORDER WHERE Status = 'PENDING';")
    
    # Extract the numbers from the dataframes
    total_patients = patients_df.iloc[0,0]
    low_stock = low_stock_df.iloc[0,0]
    pending_orders = pending_orders_df.iloc[0,0]

    # Display them in beautiful columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Registered Patients", value=total_patients, delta="Live")
    with col2:
        st.metric(label="Low Stock Alerts (< 100 units)", value=low_stock, delta="- Action Required" if low_stock > 0 else "All Good", delta_color="inverse")
    with col3:
        st.metric(label="Pending Purchase Orders", value=pending_orders)

except Exception as e:
    st.warning(f"Metrics currently unavailable. Error: {e}")

st.divider()

# 4. NAVIGATION CARDS
st.subheader("🧭 Quick Navigation")
colA, colB, colC = st.columns(3)

with colA:
    st.info("**📊 1. Dashboard**\n\nView live inventory tables and check which medications are expiring soon.")
with colB:
    st.success("**💊 2. Dispense**\n\nProcess patient prescriptions and automatically update stock levels.")
with colC:
    st.warning("**📦 3. Order Stock**\n\nCreate new purchase orders and restock low-inventory items.")

# 5. DISCREET CONNECTION STATUS (Footer)
st.markdown("<br><br>", unsafe_allow_html=True) 

try:
    conn = get_connection() # Grab the connection without the "with" block!
    with conn.cursor() as cur: # It's okay to close the cursor, just not the connection
        cur.execute("SELECT 1;")
        st.caption("🟢 System Status: Database Connected Securely")
except Exception as e:
    st.caption(f"🔴 System Status: Disconnected ({e})")