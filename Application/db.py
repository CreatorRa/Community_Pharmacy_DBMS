import os
import psycopg
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Always return a fresh connection (safe with Streamlit reruns)."""
    if not DATABASE_URL:
        st.error("Missing DATABASE_URL! Please make sure your .env file is set up correctly.")
        st.stop()
    return psycopg.connect(DATABASE_URL)

def run_query(query, params=None):
    """Safe SELECT helper that opens/closes connection each time."""
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()