import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection

# =====================================================================
# UI INITIALIZATION & CSS
# =====================================================================
st.set_page_config(page_title="Pharmacy DBMS", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
      /* Main App Background */
      [data-testid="stAppViewContainer"] { background-color: #f4f6f9; }
      [data-testid="stHeader"] { background-color: transparent; }

     /* MAIN AREA TEXT: Target paragraphs, subheaders, and spans */
      section.main title,
      section.main p,
      section.main h1, 
      section.main h2, 
      section.main h3, 
      section.main h4, 
      section.main h5, 
      section.main h6, 
      section.main span { 
      color: #000000 !important; 
      }

      /* SIDEBAR TEXT: Strictly target the sidebar and force to Pure White */
      section[data-testid="stSidebar"] p, 
      section[data-testid="stSidebar"] h1, 
      section[data-testid="stSidebar"] h2, 
      section[data-testid="stSidebar"] h3, 
      section[data-testid="stSidebar"] h4, 
      section[data-testid="stSidebar"] h5, 
      section[data-testid="stSidebar"] h6, 
      section[data-testid="stSidebar"] span,
      section[data-testid="stSidebar"] div { 
          color: #ffffff !important; 
      }

      /* KPI Card Styling with Hover Physics */
      .card {
        background: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        text-align: center;
        transition: all 0.2s ease-in-out;
      }
      .card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
          border-color: #c0c6cc;
      }
      
      /* KPI text colors (the !important tags protect them from the dark text rule above) */
      .card-title { font-size: 1.05rem; color: #5f6368 !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
      .card-value { font-size: 2.8rem; font-weight: 700; color: #0d47a1 !important; margin-top: 8px; }
      
      /* Footer Styling */
      .footer { text-align: center; font-size: 0.85rem; color: #888 !important; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# SIDEBAR BRANDING
# =====================================================================
with st.sidebar:
    st.markdown("### System Portal")
    st.markdown("Logged in as: **Admin User**")
    st.markdown("Role: **System Architect**")
    st.divider()
    st.info("Database Connection: ONLINE")
    st.caption("Version 1.0.0 | Built for PostgreSQL")

# Your excellent inline CSS fix for the title!
st.markdown("<h1 style='color: black;'>Pharmacy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: black;'>Welcome to the Central Database Portal. Monitor system health or select a quick action below.</p>", unsafe_allow_html=True)
st.divider()

# =====================================================================
# LIVE DATA AGGREGATION & RECENT ACTIVITY
# =====================================================================
@st.cache_data(ttl=60)
def fetch_landing_page_data():
    conn = get_connection()
    try:
        kpi_df = pd.read_sql("""
            SELECT 
                (SELECT COUNT(*) FROM PATIENT) AS total_patients,
                (SELECT COUNT(*) FROM PURCHASE_ORDER WHERE Status = 'PENDING') AS pending_orders,
                (SELECT COUNT(*) FROM INVENTORY_LOT WHERE Qty_on_hand < 100) AS low_stock_items,
                (SELECT COUNT(*) FROM prescription) AS total_prescriptions
        """, conn)
        
        orders_df = pd.read_sql("""
            SELECT Status, COUNT(*) as count 
            FROM PURCHASE_ORDER 
            GROUP BY Status;
        """, conn)
        
        inventory_df = pd.read_sql("""
            SELECT 
                CASE 
                    WHEN Qty_on_hand < 100 THEN 'Low Stock'
                    ELSE 'Healthy Stock'
                END AS Stock_Status,
                COUNT(*) as count
            FROM INVENTORY_LOT
            GROUP BY Stock_Status;
        """, conn)
        
        recent_rx_df = pd.read_sql("""
            SELECT 
                rx_id AS "Rx ID",
                rx_date AS "Date",
                urgency AS "Urgency",
                status AS "Status"
            FROM prescription
            ORDER BY rx_date DESC, rx_id DESC
            LIMIT 5;
        """, conn)
        
        return kpi_df.iloc[0], orders_df, inventory_df, recent_rx_df
        
    except Exception as e:
        st.error(f"Failed to fetch live database metrics: {e}")
        return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

kpis, orders_data, inventory_data, recent_rx_df = fetch_landing_page_data()

# =====================================================================
# LIVE KPI CARDS
# =====================================================================
if kpis is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    # CSS for the help icon to ensure it sits nicely next to the title
    icon_style = "cursor: help; color: #a0aab5; margin-left: 6px; font-size: 0.95rem; vertical-align: middle;"
    
    with col1:
        st.markdown(f"""
            <div class='card'>
                <div class='card-title'>
                    Total Patients 
                    <span title='Total number of registered patients in the database.' style='{icon_style}'>&#9432;</span>
                </div>
                <div class='card-value'>{kpis['total_patients']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class='card'>
                <div class='card-title'>
                    Pending Orders 
                    <span title='Orders that have been placed but not yet FULFILLED.' style='{icon_style}'>&#9432;</span>
                </div>
                <div class='card-value'>{kpis['pending_orders']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class='card'>
                <div class='card-title'>
                    Low Stock Alerts 
                    <span title='Inventory lots where the quantity on hand has dropped below 100 units.' style='{icon_style}'>&#9432;</span>
                </div>
                <div class='card-value'>{kpis['low_stock_items']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class='card'>
                <div class='card-title'>
                    Prescriptions 
                    <span title='Total number of prescriptions logged in the system.' style='{icon_style}'>&#9432;</span>
                </div>
                <div class='card-value'>{kpis['total_prescriptions']}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# CHARTS & RECENT ACTIVITY LAYOUT
# =====================================================================
left_col, right_col = st.columns([2, 1])

with left_col:
    # Notice the help="" parameter added here! It creates the (i) icon.
    st.subheader("System Overview", help="Visual breakdown of active purchase orders and current inventory health grouped by SQL aggregates.")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if not orders_data.empty:
            fig_orders = px.pie(
                orders_data, values='count', names='status', hole=0.6,
                title="Purchase Order Distribution",
                color_discrete_sequence=["#0d47a1", "#90caf9"]
            )
            fig_orders.update_traces(textinfo='percent+label')
            fig_orders.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#000000'), title_font=dict(color='#000000'))
            st.plotly_chart(fig_orders, use_container_width=True)
        else:
            st.info("No order data available.")

    with chart_col2:
        if not inventory_data.empty:
            fig_inventory = px.pie(
                inventory_data, values='count', names='stock_status', hole=0.6,
                title="Overall Inventory Health",
                color_discrete_sequence=["#e65100", "#43a047"]
            )
            fig_inventory.update_traces(textinfo='percent+label')
            fig_inventory.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#000000'), title_font=dict(color='#000000'))
            st.plotly_chart(fig_inventory, use_container_width=True)
        else:
            st.info("No inventory data available.")

with right_col:
    # Help icon added here!
    st.markdown("<h3 style='color: black;'>Recent Activity</h3>", unsafe_allow_html=True, help="A live view of the 5 most recently logged prescriptions in the database, ordered by Date descending.")
    st.markdown("<p style='color: black;'>Latest logged prescriptions</p>", unsafe_allow_html=True)
    if not recent_rx_df.empty:
        st.dataframe(recent_rx_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity found.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # =================================================================
    # QUICK ACTIONS
    # =================================================================
    # Help icon added here!
    st.subheader("Quick Actions", help="Click these links to navigate directly to the specific transaction modules required for the academic presentation.")
    try:
        # Even the links get tooltips explaining the transactions!
        st.page_link("pages/2_Dispense.py", label="Process Dispense (Tx 1 & 2)", icon="plus", help="Execute Transaction 1 (Dispensing) and Transaction 2 (Safe Reversal).")
        st.page_link("pages/3_Order.py", label="Manage Orders (Tx 3 & 4)", icon="shopping-cart", help="Execute Transaction 3 (Batch Orders) and Transaction 4 (Complex Revisions).")
        st.page_link("pages/1_Dashboard.py", label="View Inventory Data", icon="list", help="View normalized inventory and catalogue data.")
    except Exception as e:
        st.caption("Navigation links will activate once pages are fully configured.")

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("<div class='footer'>© 2026 Database Management Systems Group Project. Academic Use Only.</div>", unsafe_allow_html=True)