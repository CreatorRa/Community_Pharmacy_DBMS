import streamlit as st
from db import get_connection

# 1. Setup the Main Page Configuration
# This must be the very first Streamlit command in the file!
st.set_page_config(
    page_title="Pharmacy Management System", 
    page_icon="🏥", 
    layout="wide"
)

# 2. Welcome UI
st.title("🏥 Welcome to the Pharmacy Management System")
st.markdown("""
This application allows our pharmacy staff to manage inventory, dispense medications, and order new stock. 

👈 **Please use the sidebar menu on the left to navigate to the different tools:**
* **1_Dashboard:** View live inventory and urgent prescriptions.
* **2_Dispense:** Process new prescriptions for patients.
* **3_Order:** Create purchase orders for suppliers.
""")

st.divider()

# 3. Database Connection Test
# We test the connection right here on the home page so the team knows 
# immediately if there is a problem with their .env file!
st.subheader("System Status")

try:
    # We grab the Magic Key from db.py
    with get_connection() as conn:
        with conn.cursor() as cur:
            # A tiny query just to prove the database is awake
            cur.execute("SELECT 1;")
            result = cur.fetchone()[0]
            st.success("✅ Database Connection: Online and Ready!")
            
except Exception as e:
    st.error(f"❌ Database Connection Failed! Please check your .env file.\nError Details: {e}")
