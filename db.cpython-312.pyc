
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "app.db"

st.set_page_config(page_title="Network Error Detection Dashboard", layout="wide")

st.title("Network Error Detection Dashboard")
st.write("Basic prototype UI for monitoring endpoints and viewing check results.")

# Safety check so app doesn't crash if DB doesn't exist
if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

conn = sqlite3.connect(DB_PATH)

endpoints_df = pd.read_sql_query("SELECT * FROM endpoints", conn)
results_df = pd.read_sql_query("SELECT * FROM check_results ORDER BY id DESC", conn)

conn.close()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Endpoints")
    st.dataframe(endpoints_df, use_container_width=True)

with col2:
    st.subheader("Check Results")
    st.dataframe(results_df, use_container_width=True)

st.subheader("Summary")

total_endpoints = len(endpoints_df)
total_results = len(results_df)
ok_results = len(results_df[results_df["status"] == "OK"]) if not results_df.empty else 0
error_results = len(results_df[results_df["status"] == "ERROR"]) if not results_df.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Endpoints", total_endpoints)
c2.metric("Total Checks", total_results)
c3.metric("OK Results", ok_results)
c4.metric("Errors", error_results)
