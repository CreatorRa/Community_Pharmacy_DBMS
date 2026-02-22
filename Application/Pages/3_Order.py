import streamlit as st
import pandas as pd
from db import get_connection

# =====================================================================
# UI INITIALIZATION
# Professor, here we initialize the page layout. We use Streamlit to 
# rapidly build our frontend so we can focus on the core database logic.
# All unnecessary styling has been removed for a professional look.
# =====================================================================
st.set_page_config(page_title="Order Stock", layout="wide")
st.title("Purchase Order Management")
st.markdown("Execute **Transaction 3**: Safely create a multi-item purchase order, and monitor existing orders.")
st.divider()

# =====================================================================
# STREAMLIT TABS (PAGE WITHIN A PAGE)
# Professor, to keep the UI clean, we utilized Streamlit's tab feature. 
# This allows us to separate our Data Entry (INSERT) logic from our 
# Data Retrieval (SELECT) logic within the same module.
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["Create New Order", "Order History & Status", "Revise Order", "Cancel Order"])

# ---------------------------------------------------------------------
# TAB 1: CREATE NEW ORDER (Data Entry)
# ---------------------------------------------------------------------
with tab1:
    # =====================================================================
    # DATA FETCHING FOR DROPDOWNS
    # Professor, instead of making users guess raw Primary/Foreign Keys, 
    # we query the database upon page load to populate readable dropdown menus.
    # This ensures Referential Integrity by preventing the user from entering 
    # a Supplier or Drug ID that does not exist in the database.
    # =====================================================================
    @st.cache_data(ttl=60)
    def load_dropdown_options():
        """Fetches live suppliers and drugs from the DB to populate our menus."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Get Suppliers and format as "1001 - MediSupply"
                cur.execute("SELECT Supplier_ID, Company_name FROM SUPPLIER ORDER BY Supplier_ID;")
                supplier_opts = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                
                # 2. Get Drugs and format as "2001 - Amoxicillin"
                cur.execute("SELECT Drug_id, Drug_Name FROM DRUG_CATALOGUE ORDER BY Drug_id;")
                drug_opts = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                
            return supplier_opts, drug_opts
        except Exception as e:
            st.error(f"Failed to load dropdown data: {e}")
            return [], []

    # We execute the query and store the options BEFORE drawing the form
    supplier_options, drug_options = load_dropdown_options()

    # =====================================================================
    # BATCHING USER INPUT (THE FORM)
    # Professor, we wrap our UI in an 'st.form'. If we didn't do this, the 
    # app would try to communicate with the database every time a single 
    # character was typed. The form batches all inputs until 'Submit' is pressed.
    # =====================================================================
    with st.form("purchase_order_form"):
        
        # --- PARENT RECORD (Order Header) ---
        st.subheader("1. Order Header (Parent Record)")
        col1, col2 = st.columns(2)
        with col1:
            # The Primary Key for the parent table (PURCHASE_ORDER)
            order_id = st.number_input("New Order ID (Must be unique!)", min_value=1, value=6109) 
        with col2:
            # The Foreign Key linking back to our SUPPLIER table, displayed dynamically
            supplier_selection = st.selectbox("Select Supplier", supplier_options)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CHILD RECORDS (Order Items) ---
        st.subheader("2. Order Items (Child Records)")
        st.caption("Set quantity to 0 to skip an item.")
        
        # Safe indices to ensure we don't crash if the database has fewer than 3 drugs
        safe_index_1 = 0
        safe_index_2 = 1 if len(drug_options) > 1 else 0
        safe_index_3 = 2 if len(drug_options) > 2 else 0

        # Item 1 Row (Mandatory, minimum quantity is 1)
        col_d1, col_q1 = st.columns([2, 1])
        with col_d1:
            drug1_selection = st.selectbox("Select Drug 1", drug_options, index=safe_index_1) 
        with col_q1:
            drug1_qty = st.number_input("Drug 1 Quantity", min_value=1, value=100)

        # Item 2 Row (Optional, minimum quantity is 0)
        col_d2, col_q2 = st.columns([2, 1])
        with col_d2:
            drug2_selection = st.selectbox("Select Drug 2", drug_options, index=safe_index_2)
        with col_q2:
            drug2_qty = st.number_input("Drug 2 Quantity", min_value=0, value=250)

        # Item 3 Row (Optional, minimum quantity is 0)
        col_d3, col_q3 = st.columns([2, 1])
        with col_d3:
            drug3_selection = st.selectbox("Select Drug 3", drug_options, index=safe_index_3)
        with col_q3:
            drug3_qty = st.number_input("Drug 3 Quantity", min_value=0, value=0)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # This acts as our trigger to initiate the transaction block
        submitted = st.form_submit_button("Submit Purchase Order", type="primary")

    # =====================================================================
    # THE DATABASE TRANSACTION & RECEIPT GENERATION
    # Professor, we process this OUTSIDE the 'with st.form' block so the 
    # generated receipt prints below the form area, rather than inside it.
    # =====================================================================
    if submitted:
        
        # DATA EXTRACTION: 
        # The UI shows "1001 - MediSupply", but the database Foreign Key requires "1001".
        # We use .split(" - ") to divide the string and extract just the integer ID.
        final_supplier_id = int(supplier_selection.split(" - ")[0])
        final_drug1_id = int(drug1_selection.split(" - ")[0])
        final_drug2_id = int(drug2_selection.split(" - ")[0])
        final_drug3_id = int(drug3_selection.split(" - ")[0])
        
        conn = get_connection()
        try:
            cur = conn.cursor()
            
            # =================================================================
            # ATOMIC TRANSACTION BLOCK (ACID)
            # Professor, this demonstrates Atomicity. We must insert 1 Parent 
            # record and up to 3 Child records. They must ALL succeed, or ALL fail.
            # =================================================================
            cur.execute("BEGIN;")
            
            # 1. INSERT PARENT RECORD
            # We let PostgreSQL handle the date math natively (CURRENT_DATE + 5)
            # to satisfy the check constraint: Expected_delivery_date >= Order_date.
            cur.execute("""
                INSERT INTO PURCHASE_ORDER (Order_id, Order_date, Expected_delivery_date, Status, Supplier_ID)
                VALUES (%s, CURRENT_DATE, CURRENT_DATE + 5, 'PENDING', %s);
            """, (order_id, final_supplier_id))
            
            # 2. CONDITIONALLY INSERT CHILD RECORDS
            # We only execute the INSERT if the user requested a quantity > 0.
            # This handles the 1-to-Many relationship dynamically.
            if drug1_qty > 0:
                cur.execute("""
                    INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost)
                    VALUES (%s, %s, %s, 1.90);
                """, (order_id, final_drug1_id, drug1_qty))
                
            if drug2_qty > 0:
                cur.execute("""
                    INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost)
                    VALUES (%s, %s, %s, 0.80);
                """, (order_id, final_drug2_id, drug2_qty))
                
            if drug3_qty > 0:
                cur.execute("""
                    INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost)
                    VALUES (%s, %s, %s, 2.50); 
                """, (order_id, final_drug3_id, drug3_qty))
            
            # 3. COMMIT THE TRANSACTION
            # If no errors occurred, permanently save all records to the database.
            conn.commit()
            st.success(f"Success! Purchase Order #{order_id} has been securely saved.")
            
            # =================================================================
            # LIVE RECEIPT GENERATION
            # Professor, to prove the transaction worked, we instantly query 
            # the database using JOINs to display the newly inserted, normalized data.
            # =================================================================
            st.subheader("Order Confirmation Receipt")
            st.caption("Live data pulled directly from the database to verify the transaction.")
            
            verify_query = """
                SELECT 
                    po.Order_id AS "Order ID",
                    s.Company_name AS "Supplier",
                    po.Status AS "Status",
                    dc.Drug_Name AS "Drug Name",
                    poi.Qty_ordered AS "Quantity",
                    poi.Unit_cost AS "Unit Cost"
                FROM PURCHASE_ORDER po
                JOIN SUPPLIER s ON po.Supplier_ID = s.Supplier_ID
                JOIN PURCHASE_ORDER_ITEM poi ON po.Order_id = poi.Product_id
                JOIN DRUG_CATALOGUE dc ON poi.Drug_id = dc.Drug_id
                WHERE po.Order_id = %s;
            """
            
            # Fetch the newly created records
            cur.execute(verify_query, (order_id,))
            columns = [desc[0] for desc in cur.description]
            receipt_data = cur.fetchall()
            
            # Convert to Pandas DataFrame for a clean, read-only table
            receipt_df = pd.DataFrame(receipt_data, columns=columns)
            st.dataframe(receipt_df, use_container_width=True, hide_index=True)

        except Exception as e:
            # =================================================================
            # ERROR HANDLING & ROLLBACK
            # If the user tries to reuse an Order_id (Primary Key violation),
            # PostgreSQL throws an error. We catch it and issue a ROLLBACK to 
            # ensure no orphaned records are left in the database.
            # =================================================================
            conn.rollback()
            st.error(f"Transaction Failed & Rolled Back! The database prevented incomplete data from saving.\n\nError Details: {e}")

# ---------------------------------------------------------------------
# TAB 2: ORDER HISTORY & STATUS (Data Retrieval)
# ---------------------------------------------------------------------
with tab2:
    st.subheader("Order Monitoring")
    st.markdown("View all pending and fulfilled purchase orders in the system.")
    
    # Included CANCELLED to the list of status filters
    status_filter = st.radio(
        "Filter by Status:",
        ["All Orders", "PENDING", "FULFILLED", "CANCELLED"],
        horizontal=True
    )
    
    # =================================================================
    # FETCH ORDER HISTORY
    # Professor, we use a JOIN here to replace the numeric Supplier_ID 
    # with the actual Company Name for better user readability. 
    # =================================================================
    try:
        history_conn = get_connection()
        
        # We start with a base query
        history_query = """
            SELECT 
                po.Order_id AS "Order ID",
                s.Company_name AS "Supplier",
                po.Order_date AS "Order Date",
                po.Expected_delivery_date AS "Expected Delivery",
                po.Status AS "Status"
            FROM PURCHASE_ORDER po
            JOIN SUPPLIER s ON po.Supplier_ID = s.Supplier_ID
        """
        
        # If the user clicks a specific radio button, we append a WHERE clause
        if status_filter != "All Orders":
            history_query += f" WHERE po.Status = '{status_filter}'"
            
        # Finally, we order them so the newest orders appear at the very top
        history_query += " ORDER BY po.Order_id DESC;"
        
        # Execute query and load directly into a Pandas dataframe
        history_df = pd.read_sql(history_query, history_conn)
        
        if history_df.empty:
            st.info("No orders found matching this status.")
        else:
            # Display the interactive dataframe
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"Could not load order history: {e}")

#---------------------------------------------------------------------
# TAB 3: REVISE PURCHASE ORDER (Transaction 4)
# ---------------------------------------------------------------------
with tab3:
    st.subheader("Revise Pending Order")
    st.markdown("Execute **Transaction 4**: Modify an existing `PENDING` order by adding, updating, and removing items in one atomic block.")
    
    # =================================================================
    # LIVE DATA FETCHING
    # Professor, instead of a hardcoded demo, we query the database 
    # to find orders that are legally allowed to be edited (Status = PENDING).
    # =================================================================
    tx4_conn = get_connection()
    try:
        cur = tx4_conn.cursor()
        
        # 1. Get all pending orders
        cur.execute("SELECT Order_id FROM PURCHASE_ORDER WHERE Status = 'PENDING' ORDER BY Order_id DESC;")
        pending_orders = [row[0] for row in cur.fetchall()]
        
        if not pending_orders:
            st.info("There are currently no PENDING orders in the system. Please create one in the first tab to use this feature.")
        else:
            # Dropdown to select which order to edit
            selected_order_id = st.selectbox("Select a Pending Order to Edit", pending_orders)
            
            # 2. Fetch the items CURRENTLY inside the selected order
            cur.execute("""
                SELECT poi.Drug_id, dc.Drug_Name, poi.Qty_ordered 
                FROM PURCHASE_ORDER_ITEM poi 
                JOIN DRUG_CATALOGUE dc ON poi.Drug_id = dc.Drug_id 
                WHERE poi.Product_id = %s;
            """, (selected_order_id,))
            current_items = cur.fetchall()
            
            # Display the current state so the user knows what they are editing
            if current_items:
                st.markdown("**Current Items in Order:**")
                df_current = pd.DataFrame(current_items, columns=["Drug ID", "Drug Name", "Current Qty"])
                st.dataframe(df_current, hide_index=True)
            else:
                st.warning("This order currently contains no items.")

            # Create dynamic dropdown options based on what is currently in the order
            current_item_opts = ["None"] + [f"{r[0]} - {r[1]}" for r in current_items]
            
            # =================================================================
            # THE REVISION FORM
            # Professor, this form allows the user to queue up an INSERT, 
            # an UPDATE, and a DELETE. We batch them together so they can 
            # be processed as a single atomic transaction.
            # =================================================================
            with st.form("real_tx4_form"):
                st.markdown("### 1. Add a New Item (INSERT)")
                col1, col2 = st.columns([2, 1])
                with col1:
                    # drug_options is inherited from the top of the file!
                    add_drug = st.selectbox("Select Drug to Add", ["None"] + drug_options)
                with col2:
                    add_qty = st.number_input("Quantity to Add", min_value=0, value=0)

                st.markdown("### 2. Change an Existing Item (UPDATE)")
                col3, col4 = st.columns([2, 1])
                with col3:
                    update_drug = st.selectbox("Select Drug to Update", current_item_opts)
                with col4:
                    update_qty = st.number_input("New Quantity", min_value=0, value=0)

                st.markdown("### 3. Remove an Existing Item (DELETE)")
                delete_drug = st.selectbox("Select Drug to Remove", current_item_opts)

                st.markdown("<br>", unsafe_allow_html=True)
                submitted_tx4 = st.form_submit_button("Execute Revisions", type="primary")

            # =================================================================
            # THE TRANSACTION BLOCK
            # =================================================================
            if submitted_tx4:
                try:
                    # 🚨 BEGIN ATOMIC BLOCK 🚨
                    cur.execute("BEGIN;")
                    
                    # ACTION 1: INSERT
                    if add_drug != "None" and add_qty > 0:
                        add_id = int(add_drug.split(" - ")[0])
                        # Using 2.00 as a standard unit cost for newly added items
                        cur.execute("""
                            INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost) 
                            VALUES (%s, %s, %s, 2.00);
                        """, (selected_order_id, add_id, add_qty))
                        
                    # ACTION 2: UPDATE
                    if update_drug != "None" and update_qty > 0:
                        update_id = int(update_drug.split(" - ")[0])
                        cur.execute("""
                            UPDATE PURCHASE_ORDER_ITEM 
                            SET Qty_ordered = %s 
                            WHERE Product_id = %s AND Drug_id = %s;
                        """, (update_qty, selected_order_id, update_id))
                        
                    # ACTION 3: DELETE
                    if delete_drug != "None":
                        delete_id = int(delete_drug.split(" - ")[0])
                        cur.execute("""
                            DELETE FROM PURCHASE_ORDER_ITEM 
                            WHERE Product_id = %s AND Drug_id = %s;
                        """, (selected_order_id, delete_id))
                        
                    #COMMIT THE CHANGES
                    cur.execute("COMMIT;")
                    st.success(f"Success! Order #{selected_order_id} has been fully revised.")
                    
                    # --- LIVE RECEIPT GENERATION ---
                    st.caption("Updated Database State for this Order:")
                    cur.execute("""
                        SELECT 
                            po.Order_id AS "Order ID",
                            dc.Drug_Name AS "Drug Name",
                            poi.Qty_ordered AS "Final Quantity",
                            poi.Unit_cost AS "Unit Cost"
                        FROM PURCHASE_ORDER po
                        JOIN PURCHASE_ORDER_ITEM poi ON po.Order_id = poi.Product_id
                        JOIN DRUG_CATALOGUE dc ON poi.Drug_id = dc.Drug_id
                        WHERE po.Order_id = %s;
                    """, (selected_order_id,))
                    
                    tx4_columns = [desc[0] for desc in cur.description]
                    tx4_data = cur.fetchall()
                    
                    if tx4_data:
                        tx4_df = pd.DataFrame(tx4_data, columns=tx4_columns)
                        st.dataframe(tx4_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("This order has no items left in it.")
                        
                except Exception as e:
                    tx4_conn.rollback()
                    st.error(f"Transaction Failed & Rolled Back! The database prevented incomplete data from saving.\n\nError Details: {e}")
                    
    except Exception as e:
        st.error(f"Database connection error: {e}")

#---------------------------------------------------------------------
# TAB 4: CANCEL ORDER
# ---------------------------------------------------------------------
with tab4:
    st.subheader("Cancel Purchase Order")
    st.markdown("Select a `PENDING` purchase order to cancel it. This executes a simple **UPDATE** statement to change the order status.")
    
    cancel_conn = get_connection()
    try:
        cur = cancel_conn.cursor()
        
        # 1. Fetch only orders that are PENDING to prevent canceling fulfilled orders
        cur.execute("SELECT Order_id FROM PURCHASE_ORDER WHERE Status = 'PENDING' ORDER BY Order_id DESC;")
        cancelable_orders = [row[0] for row in cur.fetchall()]
        
        if not cancelable_orders:
            st.info("There are currently no PENDING orders available to cancel.")
        else:
            with st.form("cancel_order_form"):
                cancel_order_id = st.selectbox("Select an Order to Cancel", cancelable_orders)
                st.warning(f"Are you sure you want to cancel Order #{cancel_order_id}?")
                
                submitted_cancel = st.form_submit_button("Confirm Cancellation")
                
            if submitted_cancel:
                try:
                    cur.execute("BEGIN;")
                    
                    # Update the Status of the Parent Record to CANCELLED
                    cur.execute("""
                        UPDATE PURCHASE_ORDER 
                        SET Status = 'CANCELLED' 
                        WHERE Order_id = %s;
                    """, (cancel_order_id,))
                    
                    cur.execute("COMMIT;")
                    st.success(f"Success! Order #{cancel_order_id} has been officially CANCELLED.")
                    
                    # Prove the database was updated
                    cur.execute("SELECT Order_id, Status FROM PURCHASE_ORDER WHERE Order_id = %s;", (cancel_order_id,))
                    result = cur.fetchone()
                    st.info(f"Current Database Status for Order #{result[0]}: **{result[1]}**")
                    
                except Exception as e:
                    cancel_conn.rollback()
                    st.error(f"Failed to cancel order: {e}")
                    
    except Exception as e:
        st.error(f"Database connection error: {e}")
