import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import get_connection

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="Pharmacy Dashboard", layout="wide")

# Subtle, professional UI tweaks
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
      .card-title { font-size: 0.92rem; color: rgba(40, 42, 53, 0.9); }
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
    # Added Material Icon to the button
    if st.button(":material/refresh: Refresh data", use_container_width=True):
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
    total_patients = pd.read_sql("SELECT COUNT(*) AS n FROM PATIENT;", conn).iloc[0, 0]
    low_stock = pd.read_sql("SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Qty_on_hand < 100;", conn).iloc[0, 0]
    pending_orders = pd.read_sql("SELECT COUNT(*) AS n FROM PURCHASE_ORDER WHERE Status = 'PENDING';", conn).iloc[0, 0]
    expired_lots = pd.read_sql("SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Expiry_date < CURRENT_DATE;", conn).iloc[0, 0]
    expiring_90 = pd.read_sql("SELECT COUNT(*) AS n FROM INVENTORY_LOT WHERE Expiry_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '90 days');", conn).iloc[0, 0]

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

# Calculate dynamic health score
total_inventory_items = len(inventory)
if total_inventory_items > 0:
    # Deduct points for low stock and expired lots
    issues = low_stock_count + expired_lots
    system_health_score = max(0, 100 - int((issues / total_inventory_items) * 100))
else:
    system_health_score = 100

# ---------------------------
# KPI Cards with Alert Coloring
# ---------------------------
k1, k2, k3, k4, k5 = st.columns(5, gap="large")

def kpi_card(col, title, value, note, alert=False):
    val_color = "#d32f2f" if alert and value > 0 else "rgba(40, 42, 53, 1)"
    col.markdown(
        f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div class="card-value" style="color: {val_color};">{value}</div>
          <div class="pill">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi_card(k1, "Registered Patients", total_patients, "Live count")
kpi_card(k2, "Low Stock Items", low_stock_count, "Threshold: < 100", alert=True)
kpi_card(k3, "Pending Orders", pending_count, "Status = PENDING")
kpi_card(k4, "Expired Lots", expired_lots, "Requires action" if expired_lots > 0 else "No expired lots", alert=True)
kpi_card(k5, "Expiring in 90 Days", expiring_90, "Monitor risk", alert=True)

st.markdown("<div class='section'></div>", unsafe_allow_html=True)
st.divider()

# ---------------------------
# System Health & Inventory Filters
# ---------------------------
# Added Material Icon to header
st.subheader(":material/health_and_safety: Inventory Health Overview")

# Layout: Gauge chart on the left, filters on the right
gauge_col, filter_col = st.columns([0.35, 0.65], gap="large", vertical_alignment="center")

with gauge_col:
    # Render Plotly Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = system_health_score,
        number = {'suffix': "%"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#0d47a1"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "#ffebee"},  # Red zone
                {'range': [50, 80], 'color': "#fff8e1"},  # Yellow zone
                {'range': [80, 100], 'color': "#e8f5e9"}  # Green zone
            ]
        }
    ))
    fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with filter_col:
    f1, f2 = st.columns([0.6, 0.4], vertical_alignment="bottom")
    search = f1.text_input("Search by drug name", placeholder="Type a drug name...")
    only_low = f2.toggle("Show only low stock (<100)", value=False)

filtered = inventory.copy()

if search:
    filtered = filtered[filtered["drug_name"].str.contains(search, case=False, na=False)]
if only_low:
    filtered = filtered[filtered["qty_on_hand"] < 100]

if filtered.empty:
    st.info("No rows match your current filters. Try clearing search or turning off low-stock filter.")
    filtered = inventory.copy()

def highlight_critical(row):
    if row['expiry_date'] < pd.Timestamp.now():
        return ['background-color: #ffebee; color: #b71c1c; font-weight: bold'] * len(row)
    elif row['qty_on_hand'] < 100:
        return ['background-color: #fff8e1; color: #f57f17; font-weight: bold'] * len(row)
    return [''] * len(row)

# ---------------------------
# Tabbed Layout + Tables + Plotly Chart
# ---------------------------
# Added Material Icons to Tabs
tab1, tab2 = st.tabs([":material/list_alt: Full Inventory Directory", ":material/warning: Action Required"])

with tab1:
    st.markdown("**Current Inventory Overview**")
    styled_filtered = filtered.style.apply(highlight_critical, axis=1)
    
    st.dataframe(
        styled_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "drug_name": st.column_config.TextColumn("Drug"),
            "qty_on_hand": st.column_config.NumberColumn("Qty on hand"),
            "expiry_date": st.column_config.DateColumn("Expiry date", format="YYYY-MM-DD"),
        },
    )
    st.caption("Read-only view. Dispense and Order actions are handled in their respective pages.")

with tab2:
    col_table, col_chart = st.columns([0.4, 0.6], gap="large")
    
    top10 = inventory.sort_values("qty_on_hand", ascending=True).head(10).copy()
    styled_top10 = top10.style.apply(highlight_critical, axis=1)
    
    with col_table:
        st.markdown("**Top 10 Lowest Stock**")
        st.dataframe(
            styled_top10,
            use_container_width=True,
            hide_index=True,
            column_config={
                "drug_name": st.column_config.TextColumn("Drug"),
                "qty_on_hand": st.column_config.NumberColumn("Qty on hand"),
                "expiry_date": st.column_config.DateColumn("Expiry date", format="YYYY-MM-DD"),
            },
        )
        
    with col_chart:
        st.markdown("**Lowest Stock Trend (Snapshot)**")
        fig_bar = px.bar(
            top10, 
            x="drug_name", 
            y="qty_on_hand", 
            color="qty_on_hand",
            color_continuous_scale="Reds_r",
            labels={"drug_name": "Drug Name", "qty_on_hand": "Quantity"}
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_tickangle=-45,
            coloraxis_showscale=False 
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ---------------------------
# Footer
# ---------------------------
st.write(
    "<span class='muted'>Dashboard is a monitoring layer only (no INSERT / UPDATE / DELETE).</span>",
    unsafe_allow_html=True,
)