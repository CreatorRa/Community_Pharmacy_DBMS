import streamlit as st
import pandas as pd
import datetime as dt
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import get_connection
# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="Pharmacy Dashboard", layout="wide")

# Subtle, professional UI tweaks (no flashy emojis)
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; }
      h1, h2, h3 { letter-spacing: -0.2px; }
      .muted { color: rgba(49, 51, 63, 0.62); font-size: 0.95rem; }
      .card {
        background: #ffffff;
        border: 1px solid rgba(49, 51, 63, 0.08);
        border-radius: 16px;
        padding: 16px 16px;
        box-shadow: 0 2px 14px rgba(0,0,0,0.04);
      }
      .card-title { font-size: 0.92rem; color: rgba(49, 51, 63, 0.62); }
      .card-value { font-size: 1.9rem; font-weight: 700; margin-top: 4px; }
      .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        border: 1px solid rgba(49, 51, 63, 0.10);
        color: rgba(49, 51, 63, 0.70);
        background: rgba(49, 51, 63, 0.03);
        margin-top: 8px;
      }
      .section { margin-top: 0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Header
# ---------------------------
left, right = st.columns([0.72, 0.28], vertical_alignment="center")

with left:
    st.title("Pharmacy Operations Dashboard")
    st.write(
        "<span class='muted'>Read-only monitoring view for inventory, patients, and purchase order status.</span>",
        unsafe_allow_html=True,
    )

with right:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    st.write(
        f"<div class='muted' style='text-align:right;'>Last refreshed<br><b>{now}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ---------------------------
# Database connection
# ---------------------------
conn = get_connection()

# ---------------------------
# Data loading (cached)
# ---------------------------
@st.cache_data(ttl=60)
def load_dashboard_data():
    # KPI queries
    total_patients = pd.read_sql(
        "SELECT COUNT(*) AS n FROM PATIENT;",
        conn
    ).iloc[0, 0]

    low_stock = pd.read_sql(
        "SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Qty_on_hand < 100;",
        conn
    ).iloc[0, 0]

    pending_orders = pd.read_sql(
        "SELECT COUNT(*) AS n FROM PURCHASE_ORDER WHERE Status = 'PENDING';",
        conn
    ).iloc[0, 0]

    expired_lots = pd.read_sql(
        "SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Expiry_date < CURRENT_DATE;",
        conn
    ).iloc[0, 0]

    # Expiring soon (no UI filter, always safe)
    expiring_90 = pd.read_sql(
        "SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Expiry_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '90 days');",
        conn
    ).iloc[0, 0]

    # Inventory table
    inventory = pd.read_sql(
        """
        SELECT
            d.Drug_Name  AS drug_name,
            i.Qty_on_hand AS qty_on_hand,
            i.Expiry_date AS expiry_date
        FROM INVENTORY_LOT i
        JOIN DRUG_CATALOGUE d ON i.Drug_id = d.Drug_id
        ORDER BY i.Qty_on_hand ASC, i.Expiry_date ASC;
        """,
        conn
    )
    inventory["expiry_date"] = pd.to_datetime(inventory["expiry_date"])

    return int(total_patients), int(low_stock), int(pending_orders), int(expired_lots), int(expiring_90), inventory

total_patients, low_stock_count, pending_count, expired_lots, expiring_90, inventory = load_dashboard_data()

# ---------------------------
# KPI Cards
# ---------------------------
k1, k2, k3, k4, k5 = st.columns(5, gap="large")

def kpi_card(col, title, value, note):
    col.markdown(
        f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div class="card-value">{value}</div>
          <div class="pill">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi_card(k1, "Registered Patients", total_patients, "Live count")
kpi_card(k2, "Low Stock Items", low_stock_count, "Threshold: < 100")
kpi_card(k3, "Pending Purchase Orders", pending_count, "Status = PENDING")
kpi_card(k4, "Expired Lots", expired_lots, "Requires action" if expired_lots > 0 else "No expired lots")
kpi_card(k5, "Expiring in 90 Days", expiring_90, "Monitor expiry risk")

st.markdown("<div class='section'></div>", unsafe_allow_html=True)
st.divider()

# ---------------------------
# Inventory section (filters that will not cause 'empty' annoyance)
# ---------------------------
st.subheader("Inventory Health")

f1, f2 = st.columns([0.55, 0.45], vertical_alignment="center")
search = f1.text_input("Search by drug name", placeholder="Type a drug name…")
only_low = f2.toggle("Show only low stock (<100)", value=False)

filtered = inventory.copy()

if search:
    filtered = filtered[filtered["drug_name"].str.contains(search, case=False, na=False)]
if only_low:
    filtered = filtered[filtered["qty_on_hand"] < 100]

# Safety: never show empty without explanation
if filtered.empty:
    st.info("No rows match your current filters. Try clearing search or turning off low-stock filter.")
    filtered = inventory.copy()

# ---------------------------
# Tables + Chart
# ---------------------------
left_col, right_col = st.columns([0.62, 0.38], gap="large")

with left_col:
    st.markdown("**Current Inventory Overview**")
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "drug_name": st.column_config.TextColumn("Drug"),
            "qty_on_hand": st.column_config.NumberColumn("Qty on hand"),
            "expiry_date": st.column_config.DateColumn("Expiry date"),
        },
    )
    st.caption("Read-only view. Dispense and Order actions are handled in their respective pages.")

with right_col:
    st.markdown("**Top 10 Lowest Stock**")
    top10 = inventory.sort_values("qty_on_hand", ascending=True).head(10).copy()

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True,
        column_config={
            "drug_name": st.column_config.TextColumn("Drug"),
            "qty_on_hand": st.column_config.NumberColumn("Qty on hand"),
            "expiry_date": st.column_config.DateColumn("Expiry date"),
        },
    )

    st.markdown("**Lowest Stock Trend (Snapshot)**")
    chart_df = top10.set_index("drug_name")[["qty_on_hand"]]
    st.bar_chart(chart_df)

st.divider()

# ---------------------------
# Footer
# ---------------------------
st.write(
    "<span class='muted'>Dashboard is a monitoring layer only (no INSERT / UPDATE / DELETE).</span>",
    unsafe_allow_html=True,
)