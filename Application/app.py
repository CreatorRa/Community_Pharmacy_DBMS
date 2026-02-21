import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. PAGE CONFIGURATION (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Pharmacy Dashboard", 
    page_icon="⚕️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME TOGGLE ---
with st.sidebar:
    st.title("Settings")
    theme_mode = st.radio("Choose Theme", ["Dark", "Light"])

# Define Theme Colors
if theme_mode == "Dark":
    bg_color = "#1E1A3C"
    bg_image_css = "none"
    overlay_color = "transparent"
    card_bg = "linear-gradient(135deg, #322A5C 0%, #221D40 100%)"
    text_color = "white"
    sub_text = "#A09DB0"
    plot_bg = "#2A2548"
    border_color = "rgba(255, 255, 255, 0.05)"
    backdrop_blur = "none"
    
    # Tile variables (invisible in Dark Mode)
    tile_bg = "transparent"
    tile_blur = "none"
    tile_border = "none"
    tile_shadow = "none"
else:
    bg_color = "#F8F9FB"
    bg_image_css = "url('https://destudio.es/wp-content/uploads/2024/06/FarmaciaAnaRedondo_Web6-1.jpg')"
    # Lightened the full-page overlay so the background image is visible
    overlay_color = "rgba(248, 249, 251, 0.2)" 
    card_bg = "rgba(255, 255, 255, 0.75)"
    text_color = "#1E1A3C"
    sub_text = "#5E5E5E"
    plot_bg = "rgba(225, 228, 232, 0.5)"
    border_color = "rgba(0, 0, 0, 0.1)"
    backdrop_blur = "blur(9px)"
    
    # Frosted Glass Tile variables for Light Mode
    tile_bg = "rgba(255, 255, 255, 0.35)"
    tile_blur = "blur(4px)"
    tile_border = "1px solid rgba(255, 255, 255, 0.6)"
    tile_shadow = "0 15px 50px rgba(0, 0, 0, 0.2)"

# 2. CUSTOM CSS
st.markdown(f"""
<style>
    /* Main App Container */
    .stApp {{
        background-color: {bg_color};
        background-image: {bg_image_css};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: {text_color};
    }}
    
    /* Background Overlay */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: {overlay_color};
        /* Removed blur here so the background image stays sharp, making the frosted tile pop */
        z-index: -1;
    }}
    
    /* The Frosted Glass Tile (Main Content Container) */
    .block-container {{
        padding: 3rem !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
        background-color: {tile_bg};
        backdrop-filter: {tile_blur};
        border-radius: 24px;
        border: {tile_border};
        box-shadow: {tile_shadow};
    }}

    /* Card Styling */
    .gradient-card {{
        background: {card_bg};
        backdrop-filter: {backdrop_blur};
        border-radius: 18px;
        padding: 30px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.05);
        border: 1px solid {border_color};
        margin-bottom: 30px;
        height: 100%;
        transition: transform 0.2s ease-in-out;
    }}

    .nav-card-purple {{ background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%); }}
    .nav-card-blue {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); }}

    .card-title {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 15px;
        color: {text_color if theme_mode == "Light" else "white"};
        letter-spacing: 0.5px;
    }}

    .card-text {{
        font-size: 0.95rem;
        color: {sub_text};
        line-height: 1.6;
    }}

    h2 {{ margin-bottom: 1.5rem !important; font-weight: 800; color: {text_color} !important; }}
    h4 {{ margin-bottom: 1.2rem !important; font-weight: 600; color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# 3. HELPER FUNCTION: CREATE CIRCULAR KPI RINGS
def create_ring_chart(title, value, max_value, color, subtitle, txt_col, bg_col):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 44, 'color': txt_col, 'family': 'sans-serif'}},
        title={'text': f"<span style='font-size:18px; color:{txt_col}; font-weight:bold;'>{title}</span><br><span style='font-size:14px; color:{color}'>{subtitle}</span>"},
        gauge={
            'axis': {'range': [0, max_value], 'visible': False},
            'bar': {'color': color, 'thickness': 0.18},
            'bgcolor': bg_col,
            'borderwidth': 0,
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

# 4. DATA (Mocked)
total_patients, low_stock, pending_orders = 34, 5, 8

# 5. BUILD THE UI LAYOUT
st.markdown("<h2> Pharmacy Overview</h2>", unsafe_allow_html=True)

st.markdown("<h4> Key Performance Indicators</h4>", unsafe_allow_html=True)
kpi_col1, kpi_col2, kpi_col3 = st.columns(3, gap="large")

with kpi_col1:
    st.markdown('<div class="gradient-card">', unsafe_allow_html=True)
    st.plotly_chart(create_ring_chart("Active Patients", total_patients, 50, "#00E676", "Currently Registered", text_color, plot_bg), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_col2:
    st.markdown('<div class="gradient-card">', unsafe_allow_html=True)
    status_color = "#00E676" if low_stock == 0 else "#FFC107"
    status_text = "Inventory Stable" if low_stock == 0 else "Restock Suggested"
    st.plotly_chart(create_ring_chart("Low Stock Items", low_stock, 20, status_color, status_text, text_color, plot_bg), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_col3:
    st.markdown('<div class="gradient-card">', unsafe_allow_html=True)
    st.plotly_chart(create_ring_chart("Pending Orders", pending_orders, 15, "#FF5252", "Requiring Approval", text_color, plot_bg), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Spacing between rows
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

bottom_col1, bottom_col2 = st.columns([1, 1], gap="large")

with bottom_col1:
    nav_row1_col1, nav_row1_col2 = st.columns(2, gap="medium")
    with nav_row1_col1:
        st.markdown(f'''<div class="gradient-card nav-card-purple"><div class="card-title" style="color:white"> Inventory</div><div class="card-text" style="color:#e0e7ff">Access detailed stock levels and batch tracking.</div></div>''', unsafe_allow_html=True)
    with nav_row1_col2:
        st.markdown(f'''<div class="gradient-card nav-card-blue"><div class="card-title" style="color:white"> Dispensing</div><div class="card-text" style="color:#e0f2fe">Fulfill prescriptions and generate labels.</div></div>''', unsafe_allow_html=True)
    
    st.markdown(f'<div class="gradient-card"><div class="card-title"> Order Management System &nbsp; &nbsp; &nbsp; &nbsp; →</div></div>', unsafe_allow_html=True)

with bottom_col2:
    st.markdown('<div class="gradient-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">Order Fulfillment Timeline</div>', unsafe_allow_html=True)
    chart_data = pd.DataFrame(
        {"Orders": [4, 2, 7, 5, 12, 8, 9, 11]}, 
        index=["7am", "9am", "11am", "1pm", "3pm", "5pm", "7pm", "9pm"]
    )
    st.area_chart(chart_data, color="#6366f1")
    st.markdown('</div>', unsafe_allow_html=True)

# 6. FOOTER
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.markdown(f"<span style='color:#00E676; font-size: 14px; font-weight:bold;'>🟢 Operational</span> &nbsp; <span style='color:{sub_text}; font-size: 14px;'>| &nbsp; Last sync: Just now</span>", unsafe_allow_html=True)