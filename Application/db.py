import os
import psycopg
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. Load the secret password from your local .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Create the Database Connection
# The @st.cache_resource tells Streamlit to keep this connection open 
# so it doesn't have to log in every single time you click a button!
@st.cache_resource
def get_connection():
    if not DATABASE_URL:
        st.error("Missing DATABASE_URL! Please make sure your .env file is set up correctly.")
        st.stop() # Stops the app from crashing completely
    
    # Connect to the Neon database using psycopg 3
    return psycopg.connect(DATABASE_URL)

# 3. Create a Helper Function for your Teammate (The Watcher)
# This makes it super easy to run a SELECT query and turn the results 
# into a neat Pandas table that Streamlit can display.
def run_query(query, params=None):
    conn = get_connection()
    # pandas.read_sql perfectly formats SQL output into a data table
    return pd.read_sql(query, conn, params=params)
